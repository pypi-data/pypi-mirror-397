import json
from typing import Awaitable, Optional, Type, Any, Callable, TypedDict, Union
from collections import defaultdict
import importlib
from importlib import util as import_util
import copy
import inspect
import random

from loguru import logger
from datasets import Dataset
from xlin import xmap_async

from agentlin.route.agent_config import AgentConfig
from agentlin.evaluation.types import RolloutInput, RolloutResult, ScoreResult, EvaluationResult
from agentlin.evaluation.interface import IEvaluator


def _load_evaluator_plugin(name: Optional[str], **eval_args):
    """Best-effort attempt to load an evaluator via stevedore plugin system."""
    try:
        from stevedore import DriverManager
    except Exception as e:
        logger.debug(f"stevedore not available for evaluator: {e}")
        return None

    candidates = [c for c in [name, "default"] if c]
    for cand in candidates:
        try:
            mgr = DriverManager(
                namespace="agentlin.evaluator",
                name=cand,
                invoke_on_load=True,
                invoke_kwds=eval_args or {},
                on_load_failure_callback=lambda mgr, ep, exc: logger.debug(f"Evaluator plugin load failure: {exc}"),
            )
            evaluator = mgr.driver
            # Expect the plugin exposes evaluate/async_evaluate
            if hasattr(evaluator, "async_evaluate") or hasattr(evaluator, "evaluate"):
                logger.info(f"Using evaluator plugin: agentlin.evaluator:{cand}")
                return evaluator
        except Exception as e:
            logger.debug(f"Evaluator plugin '{cand}' not usable: {e}")
            continue
    return None


def parse_args(eval_args):
    if not eval_args:
        eval_args = "{}"
    eval_args_dict: dict = {}
    try:
        eval_args_dict: dict = json.loads(eval_args)
    except Exception as e:
        logger.error(f"Invalid eval_args JSON: {e}")
    return eval_args_dict


def _format_default(param: inspect.Parameter) -> str:
    if param.default is inspect._empty:  # type: ignore[attr-defined]
        return f"{param.name}=<required>"
    dv = param.default
    if isinstance(dv, str):
        return f"{param.name}='{dv}'"
    return f"{param.name}={dv}"


def _resolve_module_and_class(eval_path: str) -> tuple[Optional[str], Optional[str]]:
    """
    Resolve module path and optional class name from eval_path.

    Supported forms:
    - "my_eval" -> module: my_eval (if importable) or agentlin.evaluation.my_eval (fallbacks)
    - "my-eval" -> module: agentlin.evaluation.my_eval
    - "agentlin.evaluation.my_eval" -> module: agentlin.evaluation.my_eval
    - "agentlin.evaluation.my_eval:MyEvaluator" -> module + class
    - "my_eval:MyEvaluator" -> module (prefixed) + class
    - "my_eval.MyEvaluator" (discouraged) will be treated as module path if it looks like a fully-qualified path;
      prefer colon to disambiguate.
    """
    module_part = eval_path
    class_part: Optional[str] = None

    if ":" in eval_path:
        module_part, class_part = eval_path.split(":", 1)

    # normalize hyphens to underscores for module import
    module_part = module_part.replace("-", "_")

    # If it's not a fully qualified path, try unprefixed first, then fallback to agentlin.evaluation
    if not module_part.startswith("agentlin."):
        # Prefer unprefixed if it is importable on current sys.path
        try:
            if import_util.find_spec(module_part) is not None:
                return module_part, class_part
        except Exception:
            pass
        fallbacks = [
            f"agentlin.environment.{module_part}",
            f"agentlin.environments.{module_part}",
            f"agentlin.evaluation.{module_part}",
            f"agentlin.evaluations.{module_part}",
            f"env_{module_part}",
            f"agentlin_env_{module_part}",
        ]
        for fallback in fallbacks:
            try:
                if import_util.find_spec(fallback) is not None:
                    return fallback, class_part
            except Exception:
                continue

        return None, class_part

    return module_part, class_part


def _pick_evaluator_class(module, class_name: Optional[str]) -> Type[IEvaluator]:
    candidates = []
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, IEvaluator) and obj is not IEvaluator:
            candidates.append(obj)

    if class_name:
        for c in candidates:
            if c.__name__ == class_name:
                return c
        raise AttributeError(f"Class '{class_name}' not found in module '{module.__name__}' or not a subclass of IEvaluator")

    if not candidates:
        raise AttributeError(f"No IEvaluator subclass found in module '{module.__name__}'. " "Provide a load_evaluator() function or specify a class via '<module>:<ClassName>'.")

    # Heuristics: exact 'Evaluator' > name ending with 'Evaluator' > first candidate
    for c in candidates:
        if c.__name__ == "Evaluator":
            return c
    for c in candidates:
        if c.__name__.endswith("Evaluator"):
            return c
    return candidates[0]


def load_evaluator(eval_path: str, **eval_args) -> Optional[IEvaluator]:
    """
    动态加载评估器模块并实例化评估器对象。

    优先策略：
    1) 若可通过 stevedore 插件加载（agentlin.evaluator:name），先尝试插件机制（若安装了 stevedore）。
    2) 若模块定义了 load_evaluator(**kwargs)，则调用并返回结果。
    3) 否则在模块中查找 IEvaluator 的子类并尝试用 **kwargs 实例化（可通过 '<module>:<Class>' 指定类）。

    参数示例：
    - "dataset_evaluator" 或 "dataset-evaluator"
    - "agentlin.evaluation.dataset_evaluator"
    - "dataset_evaluator:DatasetEvaluator" 或 "agentlin.evaluation.dataset_evaluator:DatasetEvaluator"
    - 插件名（如已注册 stevedore entrypoint）："default"、"my-evaluator"
    """
    # Try plugin mechanism first (best-effort). If returns a valid evaluator, use it directly.
    plugin_evaluator = _load_evaluator_plugin(eval_path, **eval_args)
    if plugin_evaluator is not None:
        return plugin_evaluator

    module_name, class_name = _resolve_module_and_class(eval_path)
    if not module_name:
        logger.warning(f"Could not resolve module from eval_path '{eval_path}'")
        return None
    logger.info(f"Evaluator module name {module_name}")
    if class_name:
        logger.info(f"Requested evaluator class {class_name}")

    if eval_args:
        logger.info(f"Evaluator args provided ({len(eval_args)} total): {eval_args}")
    else:
        logger.info("No evaluator args provided, using defaults")

    try:
        module = importlib.import_module(module_name)

        # Path A: explicit module-level load_evaluator
        if hasattr(module, "load_evaluator") and inspect.isfunction(module.load_evaluator):  # type: ignore[attr-defined]
            ev_load_func = module.load_evaluator  # type: ignore[attr-defined]
            try:
                sig = inspect.signature(ev_load_func)
                defaults_info = [_format_default(param) for param in sig.parameters.values()]
                if defaults_info:
                    logger.debug("Evaluator defaults: " + ", ".join(defaults_info))

                if eval_args:
                    provided_params = set(eval_args.keys())
                    all_params = set(sig.parameters.keys())
                    default_params = all_params - provided_params
                    default_values = []
                    for name in default_params:
                        p = sig.parameters[name]
                        if p.default is not inspect._empty:  # type: ignore[attr-defined]
                            default_values.append(_format_default(p))
                    if default_values:
                        logger.info("Using defaults for: " + ", ".join(default_values))
                elif sig.parameters:
                    logger.info("All parameters will use their default values")
            except Exception as e:  # pragma: no cover - best effort logging
                logger.debug(f"Could not inspect evaluator load function signature: {e}")

            logger.debug(f"Calling {module_name}.load_evaluator with {len(eval_args)} arguments")
            ev_instance = ev_load_func(**eval_args)
            if not isinstance(ev_instance, IEvaluator):
                logger.warning(f"Object returned by {module_name}.load_evaluator is not an IEvaluator; got {type(ev_instance).__name__}")
            logger.info(f"Successfully loaded evaluator {eval_path} as {type(ev_instance).__name__}")
            return ev_instance

        # Path B: find a subclass of IEvaluator and instantiate directly
        ev_class = _pick_evaluator_class(module, class_name)
        try:
            sig = inspect.signature(ev_class)
            defaults_info = [_format_default(param) for param in list(sig.parameters.values())[1:]]  # skip 'self'
            if defaults_info:
                logger.debug(f"Constructor defaults for {ev_class.__name__}: " + ", ".join(defaults_info))
        except Exception as e:  # pragma: no cover - best effort logging
            logger.debug(f"Could not inspect constructor signature: {e}")

        # Validate required parameters
        missing_required = []
        try:
            sig = inspect.signature(ev_class)
            for name, p in list(sig.parameters.items())[1:]:  # skip 'self'
                if p.default is inspect._empty and name not in eval_args:
                    missing_required.append(name)
        except Exception:
            # If we cannot inspect, attempt best-effort construction
            pass

        if missing_required:
            raise TypeError(f"Missing required init params for {ev_class.__name__}: {', '.join(missing_required)}")

        ev_instance = ev_class(**eval_args)
        logger.info(f"Successfully loaded evaluator {eval_path} as {ev_instance.__class__.__name__}")
        return ev_instance

    except ImportError as e:
        error_message = f"Could not import '{eval_path}' evaluator. Ensure the package/module '{module_name}' is importable.\n{e}"
        logger.error(error_message)
    except Exception as e:
        error_message = f"Failed to load evaluator {eval_path} with args {eval_args}: {str(e)}"
        logger.error(error_message)
    return None


async def dataset_rollout_agent(
    inputs: Dataset,
    agent_config: AgentConfig,
    rollout_func: Union[
        Callable[[RolloutInput], RolloutResult],
        Callable[[list[RolloutInput]], list[RolloutResult]],
        Callable[[RolloutInput], Awaitable[RolloutResult]],
        Callable[[list[RolloutInput]], Awaitable[list[RolloutResult]]],
    ],
    rollout_n_per_example: int = 1,
    rollout_save_dir: Optional[str] = None,
    is_batch_rollout_func: bool = False,
    max_workers: int = -1,
    cache_path: Optional[str] = None,
    verbose: bool = True,
    **kwargs,
) -> list[RolloutResult]:
    """基于数据集执行 Agent rollout 的便捷封装（协程）。

    这是对 `dataset_rollout` 的薄封装：自动将 `agent_config` 作为任务参数
    注入到每条样本的 `task_args` 中，然后委托给 `dataset_rollout` 执行。

    Args:
        inputs: HuggingFace `datasets.Dataset`，每条样本应是 `dict`。
        agent_config: Agent 运行所需的配置对象，会合并进每条样本的 `task_args`。
        rollout_func: 单条样本的 rollout 函数，签名类似于
            `async def f(item: dict[str, Any]) -> dict[str, Any]` 或其同步版本。
            其中 `item` 至少包含 `id`, `example`, `task_args` 三个键。
        rollout_n_per_example: 每条样本重复 rollout 的次数，>1 时会对样本集进行重复。
        rollout_save_dir: 下游 `rollout_func` 可使用的保存目录（透传到 `task_args`）。
        max_workers: 并发工作线程数；<0 时按 CPU 数量自适应（min(32, cpu+4)）。
        cache_path: 可选缓存目录，若提供则 `xmap_async` 会基于 `cache_id` 去重缓存。
        verbose: 是否打印进度条等日志。
        **kwargs: 透传给 `xmap_async` 的其他参数（例如进度条、重试等）。

    Returns:
        list[dict[str, Any]]: 与 `dataset_rollout` 的返回保持一致。
            当 `rollout_n_per_example == 1` 时，返回形如：
                [{"id": str, "example": dict, "rollouts": [dict], "task_args": { ... }}, ...]
            当 `rollout_n_per_example > 1` 时，返回聚合后的结果：
                [{"id": str, "example": dict, "rollouts": [dict, ...], "task_args": { ... }}, ...]

    Notes:
        - 这是一个异步协程，需在事件循环中调用（例如 `await dataset_rollout_agent(...)`）。
        - 随机采样使用 `random.sample`，当 `num_examples` 大于数据集大小会抛出异常。
        - 缓存键使用 `"id"`，请确保每条输入的 `id` 唯一且稳定，避免缓存冲突。
    """
    return await dataset_rollout(
        inputs=inputs,
        task_args={
            "agent_config": agent_config.model_dump(),
        },
        rollout_func=rollout_func,
        rollout_n_per_example=rollout_n_per_example,
        rollout_save_dir=rollout_save_dir,
        is_batch_rollout_func=is_batch_rollout_func,
        max_workers=max_workers,
        cache_path=cache_path,
        verbose=verbose,
        **kwargs,
    )  # returns List[Dict] with keys: id, example, rollouts


async def dataset_rollout(
    inputs: Dataset,
    task_args: dict[str, Any],
    rollout_func: Union[
        Callable[[RolloutInput], RolloutResult],
        Callable[[list[RolloutInput]], list[RolloutResult]],
        Callable[[RolloutInput], Awaitable[RolloutResult]],
        Callable[[list[RolloutInput]], Awaitable[list[RolloutResult]]],
    ],
    rollout_n_per_example: int = 1,
    rollout_save_dir: Optional[str] = None,
    is_batch_rollout_func: bool = False,
    max_workers: int = -1,
    cache_path: Optional[str] = None,
    verbose: bool = True,
    **kwargs,
) -> list[RolloutResult]:
    """对数据集逐条执行 rollout，并可按样本聚合多次 rollout（协程）。

    该函数会：
    1) 当 `rollout_n_per_example > 1` 时对数据集进行重复；
    2) 为每条样本构造标准输入项：`{"id", "example", "task_args"}`，其中
       `task_args` 为传入的 `task_args` 深拷贝后与 `example.get("task_args")` 合并，
       并附加 `rollout_save_dir`；
    3) 通过 `xmap_async` 并发执行 `rollout_func`；
    4) 若进行了多次 rollout，则按同一 `example` 聚合为 `{"rollouts": [...]}` 结构。

    Args:
        inputs: HuggingFace `datasets.Dataset`，迭代返回 `dict` 的样本。
        task_args: 基础任务参数，将与样本自带的 `task_args` 合并后传给 `rollout_func`。
        rollout_func: 单条样本的 rollout 函数，支持异步或同步，批量或单条输入。
            函数将接收形如 `{ "id": str, "example": dict, "task_args": dict }` 的输入。
        rollout_n_per_example: 每条样本 rollout 的次数；>1 时会对 `inputs` 执行 `repeat()`。
        rollout_save_dir: 可选保存目录，注入到每条输入的 `task_args["rollout_save_dir"]`。
        max_workers: 并发工作线程数；<0 时按 CPU 数量自适应（min(32, cpu+4)）。
        cache_path: 可选缓存目录，启用后 `xmap_async` 会基于 `cache_id="id"` 进行缓存。
        verbose: 是否打印进度条等日志。
        **kwargs: 透传给 `xmap_async` 的额外参数（如进度、重试、超时策略等）。

    Returns:
        list[dict[str, Any]]:
            - 当 `rollout_n_per_example == 1` 时，返回 `xmap_async` 的逐条结果列表；
            - 当 `rollout_n_per_example > 1` 时，返回按样本聚合的结果，每项包含：
                {"id": str, "example": dict, "rollouts": list[dict]}。

    Raises:
        ValueError: 当 `num_examples > 0` 但其值大于数据集大小时，`random.sample` 会抛错。

    Notes:
        - 聚合阶段确定样本分组 id 的策略：优先使用 `example["id"]`；若不存在，
          使用 `int(r["id"]) % rollout_n_per_example` 的结果作为回退。
        - 为避免缓存冲突，请确保为每一条经 `repeat()` 后的输入生成唯一 `id`。
        - 这是一个异步协程，需在事件循环中调用。
    """
    if rollout_n_per_example > 1:
        inputs = inputs.repeat(rollout_n_per_example)
    if max_workers < 0:
        import multiprocessing as _multiprocessing

        max_workers = min(32, (_multiprocessing.cpu_count() or 1) + 4)

    items = []
    for i, example in enumerate(inputs):
        item = dict(
            id=str(i),
            example=example,
        )
        example_task_args = copy.deepcopy(task_args)
        example_task_args.update(example.get("task_args") or {})
        example_task_args["rollout_save_dir"] = rollout_save_dir
        item["task_args"] = example_task_args
        items.append(item)
    logger.info(f"Starting evaluation on {len(items)} items with max_workers={max_workers}")
    import inspect as _inspect

    results: list[RolloutResult] = await xmap_async(
        items,
        rollout_func,
        output_path=cache_path,
        max_workers=max_workers,
        is_batch_work_func=is_batch_rollout_func,
        is_async_work_func=_inspect.iscoroutinefunction(rollout_func),
        cache_id="id",
        verbose=verbose,
        **kwargs,
    )
    if rollout_n_per_example > 1:
        # Aggregate results by example id
        agg_results = defaultdict(list)
        for r in results:
            example = r["example"]
            eid = example["id"] if "id" in example else str(int(r["id"]) % rollout_n_per_example)
            agg_results[eid].append(r)
        results: list[RolloutResult] = []
        for eid, rs in agg_results.items():
            if len(rs) != rollout_n_per_example:
                logger.warning(f"Example id {eid} has {len(rs)} rollouts, expected {rollout_n_per_example}")
            example = rs[0]["example"]
            for r in rs:
                example = r.pop("example", example)
            results.append(RolloutResult(id=eid, example=example, rollouts=rs))
    else:
        for i, (example, r) in enumerate(zip(inputs, results)):
            if "id" not in r:
                r["id"] = str(i)
            if "example" not in r:
                r["example"] = example
            if "rollout" in r:
                r["rollouts"] = [r.pop("rollout")]
            if "rollouts" not in r:
                logger.warning(f"Result item {r.get('id', '<unknown>')} missing 'rollouts' key, adding empty list")
                r["rollouts"] = []
    return results


async def score_rollouts(
    rollouts: list[RolloutResult],  # [{"id": str, "example": example, "rollouts": [ {"id": str(inputs_idx), ...}, ... ]}, ...]
    score_func: Union[
        Callable[[RolloutResult], ScoreResult],
        Callable[[list[RolloutResult]], list[ScoreResult]],
        Callable[[RolloutResult], Awaitable[ScoreResult]],
        Callable[[list[RolloutResult]], Awaitable[list[ScoreResult]]],
    ],
    is_batch_score_func: bool = False,
    max_workers: int = -1,
    cache_path: Optional[str] = None,
    verbose: bool = True,
    **kwargs,
) -> list[ScoreResult]:
    """为 rollout 结果打分（协程）。

    使用 `xmap_async` 并发执行 `score_func` 对每个聚合项（或单条项）进行评分。
    输入通常来自 `dataset_rollout` 在 `rollout_n_per_example > 1` 时的聚合结果，
    每项形如：`{"id": str, "example": dict, "rollouts": list[dict]}`；
    若 `rollout_n_per_example == 1`，也可直接对未聚合的列表逐项评分。

    Args:
        rollouts: 需要评分的列表（聚合或未聚合的项）。
        score_func: 单项评分函数，支持异步或同步，单项或批量处理均可。
            - 单项处理签名类似于 `async def f(item: dict) -> dict` 或其同步版本；
            - 批量处理签名类似于 `async def f(items: list[dict]) -> list[dict]` 或其同步版本。
            函数应返回包含评分结果的字典，至少包含 `id`, `example`, `rollouts`, `scores` 四个键。
        is_batch_score_func: 指示 `score_func` 是否为批量处理函数。
        max_workers: 并发工作线程数；<0 时按 CPU 数量自适应（min(32, cpu+4)）。
        cache_path: 可选缓存目录，启用后 `xmap_async` 基于 `cache_id="id"` 进行缓存。

    Returns:
        list[ScoreResult]: `xmap_async` 的结果列表。典型情况下每项会包含原始输入项
        及评分相关字段（如 `reward`），具体结构取决于 `score_func` 的实现。

    Notes:
        - 这是一个异步协程，需在事件循环中调用。
        - 缓存键使用 `"id"`；请确保各项 `id` 唯一且稳定，以获得正确的缓存命中。
    """
    if max_workers < 0:
        import multiprocessing as _multiprocessing

        max_workers = min(32, (_multiprocessing.cpu_count() or 1) + 4)
    logger.info(f"Starting scoring on {len(rollouts)} items with max_workers={max_workers}")
    import inspect as _inspect

    results: list[ScoreResult] = await xmap_async(
        rollouts,
        score_func,
        output_path=cache_path,
        max_workers=max_workers,
        is_batch_work_func=is_batch_score_func,
        is_async_work_func=_inspect.iscoroutinefunction(score_func),
        cache_id="id",
        verbose=verbose,
        **kwargs,
    )
    return results
