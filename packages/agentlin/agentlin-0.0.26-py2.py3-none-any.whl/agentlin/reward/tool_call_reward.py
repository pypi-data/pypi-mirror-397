from typing import Any
from agentlin.core.types import DialogData, ToolData
from agentlin.tools.validate import validate_function_call_arguments, validate_function_call_arguments_str


def tool_call_counting_score_of_message(message: DialogData) -> float:
    tool_calls = message.get("tool_calls", [])
    if isinstance(tool_calls, list):
        return len(tool_calls)
    return 0.0


def tool_call_counting_score_of_messages(messages: list[DialogData]) -> float:
    return sum(tool_call_counting_score_of_message(m) for m in messages)


def tool_call_arguments_validation_score_of_tool_calls(
    tool_calls: list[dict[str, Any]],
    tools: list[ToolData],
) -> float:
    name2tool = {tool["function"]["name"]: tool for tool in tools}
    score = 0.0
    correct = 0
    total = 0
    for tool_call in tool_calls:
        total += 1
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("arguments")
        if not tool_name or not tool_args:
            continue
        tool_info = name2tool.get(tool_name)
        if not tool_info:
            continue
        if isinstance(tool_args, str):
            validated_args = validate_function_call_arguments_str(tool_info["function"]["parameters"], tool_args)
        else:
            validated_args = validate_function_call_arguments(tool_info["function"]["parameters"], tool_args)
        if validated_args:
            correct += 1
    if total > 0:
        score = correct / total
    return score


def tool_call_arguments_validation_score_of_message(
    message: DialogData,
    tools: list[ToolData],
) -> float:
    score = 0.0
    if "tool_calls" not in message:
        return score
    tool_calls = message["tool_calls"]
    if not isinstance(tool_calls, list):
        return score
    score = tool_call_arguments_validation_score_of_tool_calls(tool_calls, tools)
    return score


def tool_call_arguments_validation_score_of_messages(
    messages: list[DialogData],
    tools: list[ToolData],
) -> float:
    scores = []
    for m in messages:
        if m.get("role") != "assistant":
            continue
        score = tool_call_arguments_validation_score_of_message(m, tools)
        scores.append(score)
    return sum(scores) / len(scores) if scores else 0.0
