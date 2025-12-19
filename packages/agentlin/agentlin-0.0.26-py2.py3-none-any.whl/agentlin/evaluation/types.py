from typing import Optional, Type, Any, Callable, TypedDict

from agentlin.core.types import STRUCTURED_OUTPUT_TYPE, DialogData, ToolData
from agentlin.route.agent_config import AgentConfig


class TaskArgs(TypedDict):
    session_id: Optional[str]
    task_id: Optional[str]
    user_id: Optional[str]
    request_id: Optional[str]
    client_id: Optional[str]
    agent_config: Optional[AgentConfig]
    allowed_tools: Optional[list[str]]
    disallowed_tools: Optional[list[str]]
    allowed_subagents: Optional[list[str]]
    stop_tools: Optional[list[str]]
    client_tools: Optional[list[ToolData]]
    history_messages: Optional[list[DialogData]]
    thought_messages: Optional[list[DialogData]]
    structured_output: Optional[Type[STRUCTURED_OUTPUT_TYPE]]
    inference_args: Optional[dict[str, Any]]
    workspace_dir: Optional[str]
    env: Optional[dict[str, str]]
    rollout_save_dir: Optional[str]
    return_rollout: Optional[bool]


class RolloutInput(TypedDict):
    id: str
    example: dict[str, Any]

    task_args: Optional[TaskArgs]  # -> Agent __call__ kwargs
    env_args: Optional[dict[str, Any]]  # -> load_environment kwargs


class RolloutResult(TypedDict):
    id: str
    example: dict[str, Any]
    rollouts: list[dict[str, Any]]

    task_args: Optional[TaskArgs]
    env_args: Optional[dict[str, Any]]


class ScoreResult(TypedDict):
    id: str
    example: dict[str, Any]
    rollouts: list[dict[str, Any]]
    scores: list[dict[str, float]]
    avg_score: float

    task_args: Optional[TaskArgs]
    env_args: Optional[dict[str, Any]]


class EvaluationResult(TypedDict):
    evaluator: str
    avg_score: float
    rollout_with_scores: list[ScoreResult]
