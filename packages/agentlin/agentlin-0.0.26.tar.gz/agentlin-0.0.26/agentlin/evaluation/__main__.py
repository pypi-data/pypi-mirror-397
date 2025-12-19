from typing import Annotated, Optional

import typer
import asyncio
from loguru import logger
from dotenv import load_dotenv
from xlin import save_json

from agentlin.evaluation.types import EvaluationResult, TaskArgs
from agentlin.evaluation.core import load_evaluator, parse_args

app = typer.Typer()


@app.callback(invoke_without_command=True)
def evaluate(
    name: Annotated[str, typer.Option(help="Environment or Evaluator name (plugin id)")],
    agent: Annotated[str, typer.Option(help="Path to the agent config directory or file")],
    save_dir: Annotated[Optional[str], typer.Option(help="Directory to save evaluation results")] = None,
    load_args: Annotated[Optional[str], typer.Option(help="JSON string of arguments when creating evaluator instance")] = None,
    task_args: Annotated[Optional[str], typer.Option(help="JSON string of arguments passed to the evaluator.evaluate function")] = None,
    rollout_n: Annotated[int, typer.Option(help="Number of rollouts per example")] = 1,
    rollout_dir: Annotated[Optional[str], typer.Option(help="Directory to save rollouts")] = None,
    max_workers: Annotated[int, typer.Option(help="Max parallel workers (-1 auto)")] = -1,
    verbose: Annotated[bool, typer.Option(help="Whether to print progress bars and logs")] = True,
):
    """Run an evaluation by evaluator name.

    Examples:

    $ agent-eval --name gsm8k --agent ./path/to/agent/main.md --eval-args '{"split": "test"}'
    """
    load_dotenv()
    load_args_dict: dict = parse_args(load_args)
    task_args_dict: TaskArgs = parse_args(task_args)

    logger.info(f"Loading evaluator {name}")
    evaluator_obj = load_evaluator(name, **load_args_dict)
    if evaluator_obj is None:
        logger.error("No evaluator specified or failed to load evaluator.")
        return
    logger.info(f"Loaded evaluator {name}: {evaluator_obj}")

    if not hasattr(evaluator_obj, "evaluate") or not callable(evaluator_obj.evaluate):
        raise RuntimeError("Evaluator does not expose evaluate/async_evaluate")
    # Let evaluator decide dataset and strategy
    evaluation_result: EvaluationResult = evaluator_obj.evaluate(
        agent_path=agent,
        rollout_n_per_example=rollout_n,
        rollout_save_dir=rollout_dir,
        max_workers=max_workers,
        verbose=verbose,
        **task_args_dict,
    )
    save_json(evaluation_result, save_dir)


if __name__ == "__main__":
    app()
