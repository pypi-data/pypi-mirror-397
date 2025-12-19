from typing_extensions import Any, Optional

from agentlin.code_interpreter.types import MIME_TOOL_CALL, MIME_TOOL_RESPONSE, ToolCallData, ToolResponse
from agentlin.code_interpreter.display_mime import MimeDisplayObject, display



def display_tool_call(
    call_id: str,
    tool_name: str,
    tool_args: dict[str, Any],
    tool_id: Optional[str],
    tool_title: Optional[str],
    tool_icon: Optional[str],
):
    """
    Display tool call information in Jupyter notebook

    Args:
        tool_name: Name of the tool being called
        tool_args: Arguments passed to the tool
        call_id: Unique identifier for the tool call
    """
    tool_call = ToolCallData(
        call_id=call_id,
        tool_name=tool_name,
        tool_args=tool_args,
        tool_id=tool_id,
        tool_title=tool_title,
        tool_icon=tool_icon,
    )

    # Create display object that supports _repr_mimebundle_
    display_obj = MimeDisplayObject(MIME_TOOL_CALL, tool_call)
    display(display_obj)


def display_tool_response(
    message_content: list[dict[str, Any]],
    block_list: list[dict[str, Any]],
    **kwargs,
):
    """
    Display tool response data in Jupyter notebook

    Args:
        message_content: List of dictionaries containing tool response data
        block_list: List of dictionaries containing block information
        **kwargs: Additional keyword arguments
    """
    tool_response = ToolResponse(
        message_content=message_content,
        block_list=block_list,
        data=kwargs,
    )

    # Create display object that supports _repr_mimebundle_
    display_obj = MimeDisplayObject(MIME_TOOL_RESPONSE, tool_response)
    display(display_obj)


def display_internal_error(error_message: str):
    """
    Display internal error message in Jupyter notebook

    Args:
        error_message: The internal error message to display
    """
    display_tool_response(
        message_content=[{"type": "text", "text": error_message}],
        block_list=[],
    )

def display_message_content(message_content: list[dict[str, Any]]):
    """
    Display message content in Jupyter notebook

    Args:
        message_content: List of dictionaries containing message content
    """
    display_tool_response(
        message_content=message_content,
        block_list=[],
    )

def display_block(block: dict[str, Any]):
    """
    Display a single block in Jupyter notebook

    Args:
        block: Dictionary containing block information
    """
    display_tool_response(
        message_content=[],
        block_list=[block],
    )

