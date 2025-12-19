from agentlin.code_interpreter.types import ToolResponse
from agentlin.environment.interface import IStoppableState, ICount2StopState


class TextState(IStoppableState):
    text: str

    def __str__(self):
        return self.text

    def display(self) -> ToolResponse:
        if not self.check_validity():
            message = "Invalid state"
        else:
            message = self.text
        return {
            "message_content": [{"type": "text", "text": message}],
            "block_list": [{"type": "text", "text": message}],
            "data": {"done": self.done},
        }


class ErrorState(TextState):
    def __init__(self, text: str, done: bool = False):
        super().__init__(text=f"Error: {text}", done=done)


class WarningState(TextState):
    def __init__(self, text: str, done: bool = False):
        super().__init__(text=f"Warning: {text}", done=done)


class TextCount2StopState(ICount2StopState, TextState):
    def __init__(self, text: str, count: int, max_count: int, done: bool = False):
        ICount2StopState.__init__(self, count, max_count, done)
        TextState.__init__(self, text, done)

    def display(self) -> ToolResponse:
        if not self.check_validity():
            message = "Invalid state"
        elif self.done:
            message = f"{self.text}\nProgress: {self.count}/{self.max_count}. Done: {self.done}."
        else:
            message = f"{self.text}\nProgress: {self.count}/{self.max_count}. {self.max_count-self.count} steps remain. Done: {self.done}."
        return {
            "message_content": [{"type": "text", "text": message}],
            "block_list": [{"type": "text", "text": message}],
            "data": {"done": self.done},
        }


class FailExceedMaxStepState(TextCount2StopState):
    def __init__(self, count: int, max_count: int):
        assert count >= max_count
        text = f"Failed: Exceeded maximum steps. Max steps count is {max_count}. Total steps taken: {count}."
        super().__init__(text, count, max_count, done=True)

