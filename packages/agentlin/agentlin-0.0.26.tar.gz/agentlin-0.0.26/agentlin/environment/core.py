from typing import Optional, Type
import importlib
from importlib import util as import_util
import inspect

from loguru import logger

from agentlin.environment.interface import IEnvironment


def _format_default(param: inspect.Parameter) -> str:
    if param.default is inspect._empty:  # type: ignore[attr-defined]
        return f"{param.name}=<required>"
    dv = param.default
    if isinstance(dv, str):
        return f"{param.name}='{dv}'"
    return f"{param.name}={dv}"


def _resolve_module_and_class(env_path: str) -> tuple[str, Optional[str]]:
    """
    Resolve module path and optional class name from env_path.

    Supported forms:
    - "qa_env" -> module: qa_env (if importable) or agentlin.environment.qa_env (fallback)
    - "qa-env" -> module: agentlin.environment.qa_env
    - "agentlin.environment.qa_env" -> module: agentlin.environment.qa_env
    - "agentlin.environment.qa_env:QAEnv" -> module + class
    - "qa_env:QAEnv" -> module (prefixed) + class
    - "qa_env.QAEnv" (discouraged) will be treated as module path if it looks like a fully-qualified path;
      prefer colon to disambiguate.
    """
    module_part = env_path
    class_part: Optional[str] = None

    if ":" in env_path:
        module_part, class_part = env_path.split(":", 1)

    # normalize hyphens to underscores for module import
    module_part = module_part.replace("-", "_")

    # If it's not a fully qualified path, try unprefixed first, then fallback to agentlin.environment
    if not module_part.startswith("agentlin."):
        # Prefer unprefixed if it is importable on current sys.path
        try:
            if import_util.find_spec(module_part) is not None:
                return module_part, class_part
        except Exception:
            pass
        fallbacks = [
            f"agentlin.environment.builtin.{module_part}",
            f"agentlin.environment.{module_part}",
            f"env_{module_part}",
        ]
        for fallback in fallbacks:
            # If fallback exists, use it; otherwise still return fallback and let caller raise a clear error
            try:
                if import_util.find_spec(fallback) is not None:
                    return fallback, class_part
            except Exception:
                continue
        return fallback, class_part

    return module_part, class_part


def _pick_env_class(module, class_name: Optional[str]) -> Type[IEnvironment]:
    candidates = []
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, IEnvironment) and obj is not IEnvironment:
            candidates.append(obj)

    if class_name:
        for c in candidates:
            if c.__name__ == class_name:
                return c
        raise AttributeError(f"Class '{class_name}' not found in module '{module.__name__}' or not a subclass of IEnvironment")

    if not candidates:
        raise AttributeError(f"No IEnvironment subclass found in module '{module.__name__}'. Provide a load_environment() function or specify a class via '<module>:<ClassName>'.")

    # Heuristics: exact 'Env' > name ending with 'Env' > first candidate
    for c in candidates:
        if c.__name__ == "Env":
            return c
    for c in candidates:
        if c.__name__.endswith("Env"):
            return c
    return candidates[0]


def _try_load_local_environment(env_path: str) -> Optional[str]:
    """
    尝试从指定路径加载本地环境。

    支持的路径格式：
    - 相对路径：environments/arc-agi-3, ./environments/gsm8k
    - 绝对路径：/path/to/env_dir

    如果路径指向一个有效的环境目录：
    1. 将环境目录添加到 sys.path
    2. 返回可导入的模块名（env_* 格式）

    返回 None 表示不是本地路径或找不到有效环境。
    """
    import sys
    from pathlib import Path

    # 提取路径（去除可能的类名后缀）
    base_path = env_path.split(":")[0] if ":" in env_path else env_path

    # 判断是否看起来像一个路径（包含 / 或 \ 或以 . 开头）
    if not ("/" in base_path or "\\" in base_path or base_path.startswith(".")):
        return None

    try:
        # 解析路径
        env_dir = Path(base_path).resolve()

        # 检查目录是否存在
        if not env_dir.exists() or not env_dir.is_dir():
            logger.debug(f"Path {env_dir} does not exist or is not a directory")
            return None

        # 查找 env_* 模块
        env_module_name = None
        for item in env_dir.iterdir():
            # 查找 env_*.py 文件
            if item.is_file() and item.suffix == ".py" and item.stem.startswith("env_"):
                env_module_name = item.stem
                break
            # 查找 env_*/ 包
            if item.is_dir() and item.name.startswith("env_") and (item / "__init__.py").exists():
                env_module_name = item.name
                break

        if not env_module_name:
            logger.debug(f"Directory {env_dir} found, but no env_* module found (files: {[f.name for f in env_dir.iterdir()]})")
            return None

        # 将环境目录添加到 sys.path（如果尚未添加）
        env_dir_str = str(env_dir)
        if env_dir_str not in sys.path:
            sys.path.insert(0, env_dir_str)
            logger.debug(f"Added {env_dir_str} to sys.path")

        logger.info(f"Found local environment module: {env_module_name} in {env_dir}")
        return env_module_name

    except Exception as e:
        logger.debug(f"Error while trying to load local environment from path {base_path}: {e}")
        return None


def load_environment(env_path: str, **env_args) -> IEnvironment:
    """
    动态加载环境模块并实例化环境对象。

    优先策略：
    1) 若 env_path 是路径（包含 / 或 \），则从该路径加载本地环境
    2) 若模块定义了 load_environment(**kwargs)，则调用并返回结果
    3) 否则在模块中查找 IEnvironment 的子类并尝试用 **kwargs 实例化（可通过 '<module>:<Class>' 指定类）

    参数示例：
    - "qa_env" 或 "qa-env" (模块名)
    - "agentlin.environment.qa_env" (完整模块路径)
    - "qa_env:QAEnv" 或 "agentlin.environment.qa_env:QAEnv" (指定类)
    - "environments/arc-agi-3" (本地路径 - 相对路径)
    - "./environments/gsm8k" (本地路径 - 相对路径)
    - "/absolute/path/to/env_dir" (本地路径 - 绝对路径)
    - "environments/arc-agi-3:ArcAgi3" (本地路径 + 指定类)
    """
    logger.info(f"Loading environment {env_path}")

    # Try to load from local path first (if env_path looks like a path)
    local_env_module = _try_load_local_environment(env_path)
    if local_env_module:
        module_name = local_env_module
        class_name = None
        if ":" in env_path:
            _, class_name = env_path.split(":", 1)
        logger.info(f"Loading from local path: {module_name}")
    else:
        module_name, class_name = _resolve_module_and_class(env_path)
        logger.info(f"Environment module name {module_name}")

    if class_name:
        logger.info(f"Requested environment class {class_name}")

    if env_args:
        logger.info(f"Environment args provided ({len(env_args)} total): {env_args}")
    else:
        logger.info("No environment args provided, using defaults")

    try:
        module = importlib.import_module(module_name)

        # Path A: explicit module-level load_environment
        if hasattr(module, "load_environment") and inspect.isfunction(module.load_environment):  # type: ignore[attr-defined]
            env_load_func = module.load_environment  # type: ignore[attr-defined]
            try:
                sig = inspect.signature(env_load_func)
                defaults_info = [_format_default(param) for param in sig.parameters.values()]
                if defaults_info:
                    logger.debug("Environment defaults: " + ", ".join(defaults_info))

                if env_args:
                    provided_params = set(env_args.keys())
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
                logger.debug(f"Could not inspect environment load function signature: {e}")

            logger.debug(f"Calling {module_name}.load_environment with {len(env_args)} arguments")
            env_instance = env_load_func(**env_args)
            if not isinstance(env_instance, IEnvironment):
                logger.warning(f"Object returned by {module_name}.load_environment is not an IEnvironment; got {type(env_instance).__name__}")
            logger.info(f"Successfully loaded environment {env_path} as {type(env_instance).__name__}")
            return env_instance

        # Path B: find a subclass of IEnvironment and instantiate directly
        env_class = _pick_env_class(module, class_name)
        try:
            sig = inspect.signature(env_class)
            defaults_info = [_format_default(param) for param in list(sig.parameters.values())[1:]]  # skip 'self'
            if defaults_info:
                logger.debug(f"Constructor defaults for {env_class.__name__}: " + ", ".join(defaults_info))
        except Exception as e:  # pragma: no cover - best effort logging
            logger.debug(f"Could not inspect constructor signature: {e}")

        # Validate required parameters
        missing_required = []
        try:
            sig = inspect.signature(env_class)
            for name, p in list(sig.parameters.items())[1:]:  # skip 'self'
                if p.default is inspect._empty and name not in env_args:
                    missing_required.append(name)
        except Exception:
            # If we cannot inspect, attempt best-effort construction
            pass

        if missing_required:
            raise TypeError(f"Missing required init params for {env_class.__name__}: {', '.join(missing_required)}")

        env_instance = env_class(**env_args)
        logger.info(f"Successfully loaded environment {env_path} as {env_instance.__class__.__name__}")
        return env_instance

    except ImportError as e:
        error_message = f"Could not import '{env_path}' environment. Ensure the package/module '{module_name}' is importable.\n{e}"
        logger.error(error_message)
        raise ValueError(error_message) from e
    except Exception as e:
        error_message = f"Failed to load environment {env_path} with args {env_args}: {str(e)}"
        logger.error(error_message)
        raise RuntimeError(error_message) from e


def list_environments() -> list[str]:
    """
    列出可用的环境名称。

    搜索范围与约定：
    - 内置模块包：agentlin.environment 以及 agentlin.environment.builtin 下的模块
      满足以下任一条件即视为环境模块：
        1) 模块中存在函数 load_environment
        2) 模块中定义了 IEnvironment 的子类
    - 系统可导入的顶层模块名形如 env_*（例如 env_arc_agi_3、env_gsm8k）
      会转换为友好名称（将前缀 env_ 去掉，下划线转连字符），如 arc-agi-3、gsm8k。
    - 工作区本地目录 environments/*（如果存在），若子目录内含有以 env_ 开头的包或 .py 文件，
      则将该子目录名加入列表（用于提示本地可安装的环境）。

    返回：
        环境名称的去重列表，已按字母排序。
    """
    details = list_environments_detailed()
    names = sorted({d["name"] for d in details})
    return names


def list_environments_detailed() -> list[dict[str, Optional[str]]]:
    """
    返回包含详细信息的环境列表，用于 UI/CLI 展示与去重判断。

    字段：
    - name: 友好名称（如 'qa_env', 'arc-agi-3'）
    - module: 完整模块路径（如 'agentlin.environment.qa_env' 或 'env_gsm8k'），本地目录则可能为 None
    - origin: 'builtin' | 'external' | 'local'
    - source: 内部源标识（如 'package:agentlin.environment', 'package:agentlin.environment.builtin', 'import:env_*', 'local:environments/<dir>'）
    - importable: bool 是否可被 importlib 正常导入
    - classes: IEnvironment 子类名列表
    - has_factory: 是否存在模块级 load_environment
    - default_params_summary: 从类构造器或工厂函数推断的默认参数摘要（简要字符串）
    - prefer: 推荐加载标识（通常与 name 相同，可作为 load_environment 的参数）
    """
    import pkgutil
    from pathlib import Path

    results: list[dict] = []

    EXCLUDE_BUILTIN_NAMES = {
        "__main__",
        "__init__",
        "core",  # 加载器，不是具体环境
        "interface",
        "state",
    }

    def _inspect_module(module_name: str) -> tuple[bool, list[str], bool, str]:
        """返回 (has_env, class_names, has_factory, default_params_summary)。
        对于 builtin 包内模块，只有存在 IEnvironment 子类时才认为是有效环境，避免 'core' 之类误判。
        对于外部 env_* 包，工厂或子类任何一种即可。
        """
        try:
            mod = importlib.import_module(module_name)
        except Exception:
            return False, [], False, ""

        has_factory = hasattr(mod, "load_environment") and inspect.isfunction(getattr(mod, "load_environment", None))
        class_names: list[str] = []
        for _, obj in inspect.getmembers(mod, inspect.isclass):
            try:
                if inspect.isabstract(obj):
                    continue
                if issubclass(obj, IEnvironment) and obj is not IEnvironment:
                    class_names.append(obj.__name__)
            except Exception:
                continue

        default_summary = ""
        # 优先展示工厂函数参数，其次展示首个类构造参数
        if has_factory:
            try:
                sig = inspect.signature(getattr(mod, "load_environment"))
                parts = [_format_default(p) for p in sig.parameters.values()]
                default_summary = ", ".join(parts)
            except Exception:
                pass
        elif class_names:
            try:
                cls = getattr(mod, class_names[0])
                sig = inspect.signature(cls)
                parts = [_format_default(p) for p in list(sig.parameters.values())[1:]]  # 跳过 self
                default_summary = ", ".join(parts)
            except Exception:
                pass

        # 是否有效环境：由调用方告知上下文；这里默认：有类即有效；否则用 has_factory
        has_env = len(class_names) > 0 or has_factory
        return has_env, class_names, has_factory, default_summary

    # 1) builtin: agentlin.environment
    try:
        import agentlin.environment as _env_pkg  # type: ignore
        for mod_info in pkgutil.iter_modules(_env_pkg.__path__):  # type: ignore[attr-defined]
            base = mod_info.name
            if base in EXCLUDE_BUILTIN_NAMES:
                continue
            full = f"{_env_pkg.__name__}.{base}"
            has_env, class_names, has_factory, default_summary = _inspect_module(full)
            # 内置包必须有 IEnvironment 子类，避免 core 之类
            if class_names:
                results.append({
                    "name": base,
                    "module": full,
                    "origin": "builtin",
                    "source": "package:agentlin.environment",
                    "importable": import_util.find_spec(full) is not None,
                    "classes": class_names,
                    "has_factory": has_factory,
                    "default_params_summary": default_summary,
                    "prefer": base,
                })
    except Exception:
        pass

    # 1b) builtin: agentlin.environment.builtin
    try:
        import agentlin.environment.builtin as _builtin_pkg  # type: ignore
        for mod_info in pkgutil.iter_modules(_builtin_pkg.__path__):  # type: ignore[attr-defined]
            base = mod_info.name
            if base in EXCLUDE_BUILTIN_NAMES:
                continue
            full = f"{_builtin_pkg.__name__}.{base}"
            has_env, class_names, has_factory, default_summary = _inspect_module(full)
            if class_names:
                results.append({
                    "name": base,
                    "module": full,
                    "origin": "builtin",
                    "source": "package:agentlin.environment.builtin",
                    "importable": import_util.find_spec(full) is not None,
                    "classes": class_names,
                    "has_factory": has_factory,
                    "default_params_summary": default_summary,
                    "prefer": base,
                })
    except Exception:
        pass

    # 2) external: 顶层 env_* 包
    try:
        for _finder, name, _ispkg in pkgutil.iter_modules():
            if not name.startswith("env_"):
                continue
            full = name
            has_env, class_names, has_factory, default_summary = _inspect_module(full)
            if has_env:
                friendly = name[len("env_"):].replace("_", "-")
                results.append({
                    "name": friendly,
                    "module": full,
                    "origin": "external",
                    "source": "import:env_*",
                    "importable": import_util.find_spec(full) is not None,
                    "classes": class_names,
                    "has_factory": has_factory,
                    "default_params_summary": default_summary,
                    "prefer": friendly,  # 友好名可直接用于 load_environment
                })
    except Exception:
        pass

    # 3) local: 工作区 environments 目录
    try:
        current_file = Path(__file__).resolve()
        repo_root = current_file
        for _ in range(5):
            if (repo_root / "pyproject.toml").exists() or (repo_root / ".git").exists():
                break
            repo_root = repo_root.parent

        local_envs_dir = repo_root / "environments"
        if local_envs_dir.exists() and local_envs_dir.is_dir():
            for child in local_envs_dir.iterdir():
                if not child.is_dir():
                    continue
                # 查找 env_*
                has_env_file = False
                env_entry = None
                for p in child.iterdir():
                    if p.is_file() and p.suffix == ".py" and p.stem.startswith("env_"):
                        has_env_file = True
                        env_entry = p.name
                        break
                    if p.is_dir() and p.name.startswith("env_") and (p / "__init__.py").exists():
                        has_env_file = True
                        env_entry = p.name
                        break
                if has_env_file:
                    results.append({
                        "name": child.name,
                        "module": None,
                        "origin": "local",
                        "source": f"local:environments/{child.name}",
                        "importable": False,
                        "classes": [],
                        "has_factory": False,
                        "default_params_summary": "",
                        "prefer": child.name,
                    })
    except Exception:
        pass

    # 去除明显的伪项：__main__ 之类（双重保险）
    results = [r for r in results if r.get("name") not in {"__main__", "__init__"}]

    # 排序：按 name, origin
    results.sort(key=lambda r: (r.get("name", ""), r.get("origin", "")))
    return results
