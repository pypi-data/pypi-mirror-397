from typing import Callable, Union

from agentlin.core.types import ContentData
from agentlin.reward.base import compute_binary_score, compute_binary_score_of_messages
from agentlin.reward.grade_think_format import validate_boxed_answer_format, validate_think_format, validate_think_answer_format


def compute_format_score(content: Union[str, list[ContentData]], validate_format_func: Callable[[str], bool]) -> float:
    return compute_binary_score(content, validate_format_func)


def compute_format_score_of_messages(messages: list[ContentData], validate_format_func: Callable[[str], bool]) -> float:
    return compute_binary_score_of_messages(messages, validate_format_func)


def compute_think_format_score(content: Union[str, list[ContentData]]) -> float:
    return compute_format_score(content, validate_think_format)


def compute_think_format_score_of_messages(messages: list[ContentData]) -> float:
    return compute_format_score_of_messages(messages, validate_think_format)


def compute_think_answer_format_score(content: Union[str, list[ContentData]]) -> float:
    return compute_format_score(content, validate_think_answer_format)


def compute_think_answer_format_of_messages(messages: list[ContentData]) -> float:
    return compute_format_score_of_messages(messages, validate_think_answer_format)


def compute_boxed_answer_format_score(content: Union[str, list[ContentData]]) -> float:
    return compute_format_score(content, validate_boxed_answer_format)


def compute_boxed_answer_format_of_messages(messages: list[ContentData]) -> float:
    return compute_format_score_of_messages(messages, validate_boxed_answer_format)


def compute_think_boxed_answer_format_score(content: Union[str, list[ContentData]]) -> float:
    return compute_format_score(content, lambda x: validate_think_format(x) and validate_boxed_answer_format(x))


def compute_think_boxed_answer_format_of_messages(messages: list[ContentData]) -> float:
    return compute_format_score_of_messages(messages, lambda x: validate_think_format(x) and validate_boxed_answer_format(x))
