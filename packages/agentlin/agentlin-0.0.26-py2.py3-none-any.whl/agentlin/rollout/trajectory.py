from typing_extensions import TypeVar
from pydantic import BaseModel

from xlin import append_to_json_list, load_json_list

from agentlin.core.types import TaskRolloutEvent

ENV_STATE = TypeVar("ENV_STATE", bound=BaseModel)

class Step(BaseModel):
    old_state: ENV_STATE
    new_state: ENV_STATE
    rollouts: list[TaskRolloutEvent] = []

class Trajectory(BaseModel):
    steps: list[Step] = []

    def append(self, step: Step):
        self.steps.append(step)

    def extend(self, steps: list[Step]):
        self.steps.extend(steps)

    def save_to_jsonl(self, filename: str):
        data = [step.model_dump() for step in self.steps]
        append_to_json_list(data, filename)

    @classmethod
    def from_jsonl(cls, filename: str) -> "Trajectory":
        data = load_json_list(filename)
        steps = [TaskRolloutEvent.model_validate(item) for item in data]
        return cls(steps=steps)

