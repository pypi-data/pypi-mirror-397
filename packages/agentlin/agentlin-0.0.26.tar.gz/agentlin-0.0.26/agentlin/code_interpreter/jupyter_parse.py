from typing_extensions import Literal, Optional, Union
import json
import re
import io
from plotly import graph_objects as go
from plotly import io as pio
from PIL import Image
from loguru import logger

from agentlin.code_interpreter.data_to_visual_json import AiVisual
from agentlin.core.multimodal import image_content
from agentlin.core.agent_schema import content_to_text, generate_short_embed_id, generate_short_uuid
from agentlin.code_interpreter.types import (
    MIME_MARKDOWN,
    MIME_TEXT,
    MIME_IMAGE_PNG,
    MIME_IMAGE_JPEG,
    MIME_PLOTLY,
    TYPE_TABLE,
    MIME_TABLE_V1,
    MIME_TABLE_V2,
    MIME_TABLE_V3,
    TYPE_DOCUMENT,
    MIME_DOCUMENT,
    MIME_HTML,
    MIME_TOOL_CALL,
    MIME_TOOL_RESPONSE,
    TYPE_SEARCH_RESULT,
    MIME_SEARCH_RESULT,
    MIME_SEARCH_RESULT_LIST,
    TYPE_VISUAL,
    MIME_VISUAL,
    VisualDataV1,
    SearchResult,
    ToolResponse,
    is_block_json_version,
)
from agentlin.code_interpreter.display_search_result import search_result_to_text


def delete_color_control_char(string: str) -> str:
    ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    return ansi_escape.sub("", string)


def text_response(iopub_msg: dict, text: str) -> ToolResponse:
    return {
        "message_content": [{"type": "text", "text": text}],
        "block_list": [{"type": "text", "text": text}],
        "iopub_messages": [iopub_msg],
    }

def image_response(iopub_msg: dict, image_url: str, **kwargs) -> ToolResponse:
    uuid: int = kwargs.get("uuid", None)
    if not uuid:
        uuid = generate_short_uuid()
    return {
        "message_content": image_content(image_url, uuid),
        "block_list": [{"type": "image_url", "image_url": {"url": image_url}, "id": uuid}],
        "iopub_messages": [iopub_msg],
    }

def html_response(iopub_msg: dict, text: Union[list[str], str], **kwargs) -> ToolResponse:
    if isinstance(text, list):
        text = "".join(text)
    uuid = kwargs.get("uuid", None)
    if not uuid:
        uuid = generate_short_uuid()
    return {
        "message_content": [{"type": "text", "text": f"```html\n{text}\n```", "id": uuid}],
        "block_list": [{"type": "html", "data": {MIME_HTML: text}, "id": uuid}],
        "iopub_messages": [iopub_msg],
    }

def plotly_response(iopub_msg: dict, fig_json: dict, **kwargs) -> ToolResponse:
    uuid: int = kwargs.get("uuid", None)
    if not uuid:
        uuid = generate_short_uuid()
    if isinstance(fig_json, dict):
        fig = go.Figure(fig_json)
    else:
        fig = pio.from_json(fig_json)

    # Convert to image bytes using plotly
    img_bytes = pio.to_image(fig, format="png")
    image = Image.open(io.BytesIO(img_bytes))
    return {
        "message_content": image_content(image, uuid),
        "block_list": [
            {
                "type": "plotly-json",
                "data": {MIME_PLOTLY: fig_json},
                "id": uuid,
            }
        ],
        "iopub_messages": [iopub_msg],
    }

def table_response(iopub_msg: dict, data: dict, **kwargs) -> ToolResponse:
    text = data.get("text/plain", "empty table")
    block = {
        "type": TYPE_TABLE,
        "data": {},
    }
    table_data = None
    if MIME_TABLE_V1 in data:
        table_data = data[MIME_TABLE_V1]
        block["data"][MIME_TABLE_V1] = table_data
    elif MIME_TABLE_V2 in data:
        table_data = data[MIME_TABLE_V2]
        block["data"][MIME_TABLE_V2] = table_data
    elif MIME_TABLE_V3 in data:
        table_data = data[MIME_TABLE_V3]
        block["data"][MIME_TABLE_V3] = table_data
    elif is_block_json_version(data, type="table"):
        for k in data:
            if k.startswith("application/vnd.aime.table"):
                table_data = data[k]
                block["data"][k] = table_data
                break
    else:
        table_data = {"columns": [], "datas": []}
        block["data"][MIME_TABLE_V2] = table_data
    uuid = generate_short_uuid()
    block["id"] = uuid
    if isinstance(table_data, dict) and "text" in table_data:
        text = table_data.get("text", "empty table")
    if "data" in block and isinstance(block["data"], dict):
        if "text" in block["data"]:
            del block["data"]["text"]
        if "query_id" in block["data"]:
            block["id"] = block["data"]["query_id"]
            del block["data"]["query_id"]

    return {
        "message_content": [{"type": "text", "text": text, "id": block["id"]}],
        "block_list": [block],
        "iopub_messages": [iopub_msg],
    }


def search_result_response(iopub_msg: dict, data: dict, **kwargs) -> ToolResponse:
    """Handle search result or search result list MIME bundles.

    Expected formats (already in iopub_msg['content']['data']):
    - MIME_SEARCH_RESULT: { ...SearchResult fields... }
    - MIME_SEARCH_RESULT_LIST: {"search_results": [SearchResult, ...]}
    """
    raw_single: Optional[SearchResult] = data.get(MIME_SEARCH_RESULT)
    raw_list: Optional[dict[Literal["search_results"], list[SearchResult]]] = data.get(MIME_SEARCH_RESULT_LIST)

    block_list = []
    message_content = []

    if raw_single is not None:
        sr = dict(raw_single)
        if not isinstance(sr.get("id"), int):
            sr["id"] = 0
        block_list.append({
            "type": TYPE_SEARCH_RESULT,
            "data": {MIME_SEARCH_RESULT: sr},
            "id": sr["id"],
        })
        text = search_result_to_text(sr)
        message_content.append({
            "type": "text",
            "text": text,
            "id": sr["id"],
        })

    if raw_list is not None:
        results = raw_list.get("search_results", []) if isinstance(raw_list, dict) else []
        for idx, item in enumerate(results):
            text = search_result_to_text(item)
            # MIME_SEARCH_RESULT
            block_list.append({
                "type": TYPE_SEARCH_RESULT,
                "data": {MIME_SEARCH_RESULT: item},
                "id": item.get("id", idx),
            })
            message_content.append({
                "type": "text",
                "text": text,
                "id": item.get("id", idx),
            })

    return {
        "message_content": message_content,
        "block_list": block_list,
        "iopub_messages": [iopub_msg],
    }


def visual_response(iopub_msg: dict, data: dict, **kwargs) -> ToolResponse:
    message_content = []
    block_list = []
    if MIME_VISUAL in data:
        aivisual_dict = data[MIME_VISUAL]
        visual_object = AiVisual.model_validate(aivisual_dict)
        if visual_object.config and visual_object.image_url:
            # 有图片和 config，说明渲染成功
            reference_id = generate_short_uuid()
            # 1. 给模型看的
            if visual_object.message:
                message_content.append({"type": "text", "text": visual_object.message, "id": reference_id})
            message_content.append({"type": "image_url", "image_url": {"url": visual_object.image_url}, "id": reference_id})
            # 2. 给前端渲染的
            block = {
                "type": TYPE_VISUAL,
                "data": {
                    MIME_VISUAL: visual_object.to_visual_data(),
                },
                "id": reference_id,
            }
            block_list.append(block)
        else:
            # 没有图片或 config，说明渲染失败
            if visual_object.message:
                # 内部给出错误信息
                message_content.append({"type": "text", "text": visual_object.message})
            else:
                # 内部没有错误信息，给个固定话术作为错误信息
                message_content.append({"type": "text", "text": "Internal error occurred. Please avoid using this chart."})
    else:
        message_content.append({"type": "text", "text": "Internal error occurred. Please avoid using this chart."})
    return {
        "message_content": message_content,
        "block_list": block_list,
        "iopub_messages": [iopub_msg],
    }


def iopub_msg_to_tool_response(iopub_msg: Optional[dict], mode: Literal["simple", "full", "debug"]) -> Optional[ToolResponse]:
    """
    Convert iopub message to a ToolResponse format.
    """
    if not iopub_msg:
        return None
    if iopub_msg["msg_type"] == "stream":
        if iopub_msg["content"].get("name") == "stdout":
            output = iopub_msg["content"]["text"]
            return text_response(iopub_msg, text=delete_color_control_char(output))
    elif iopub_msg["msg_type"] == "execute_result":
        if "data" in iopub_msg["content"]:
            data = iopub_msg["content"]["data"]
            output = None
            if MIME_TOOL_RESPONSE in data or is_block_json_version(data, type="tool_response"):
                tool_response = data[MIME_TOOL_RESPONSE]
                return {
                    **tool_response,
                    "iopub_messages": [iopub_msg],
                }
            elif MIME_TOOL_CALL in data or is_block_json_version(data, type="tool_call"):
                return {
                    "message_content": [],
                    "block_list": [{
                        "type": "tool_call",
                        "data": data,
                    }],
                    "iopub_messages": [iopub_msg],
                }
            elif MIME_PLOTLY in data or is_block_json_version(data, type="plotly-json"):
                fig_json = data[MIME_PLOTLY]
                return plotly_response(iopub_msg, fig_json=fig_json)
            elif MIME_TABLE_V1 in data or MIME_TABLE_V2 in data or MIME_TABLE_V3 in data or is_block_json_version(data, type="table"):
                return table_response(iopub_msg, data=data)
            elif MIME_VISUAL in data or is_block_json_version(data, type="visual"):
                return visual_response(iopub_msg, data=data)
            elif MIME_SEARCH_RESULT in data or MIME_SEARCH_RESULT_LIST in data or is_block_json_version(data, type="search_result"):
                return search_result_response(iopub_msg, data=data)
            elif MIME_MARKDOWN in data:
                output = data[MIME_MARKDOWN]
                return text_response(iopub_msg, text=delete_color_control_char(output))
            elif MIME_IMAGE_PNG in data:
                output = data[MIME_IMAGE_PNG]
                output = "data:image/png;base64," + output
                return image_response(iopub_msg, image_url=output)
            elif MIME_IMAGE_JPEG in data:
                output = data[MIME_IMAGE_JPEG]
                output = "data:image/jpeg;base64," + output
                return image_response(iopub_msg, image_url=output)
            elif MIME_HTML in data:
                output = data[MIME_HTML]
                return html_response(iopub_msg, text=output)
            elif MIME_TEXT in data:
                output = data[MIME_TEXT]
                return text_response(iopub_msg, text=delete_color_control_char(output))
            else:
                logger.warning("content type not supported in execute_result")
                logger.warning(data)
    elif iopub_msg["msg_type"] == "display_data":
        if "data" in iopub_msg["content"]:
            data = iopub_msg["content"]["data"]
            output = None
            if MIME_TOOL_RESPONSE in data or is_block_json_version(data, type="tool_response"):
                tool_response = data[MIME_TOOL_RESPONSE]
                return {
                    **tool_response,
                    "iopub_messages": [iopub_msg],
                }
            elif MIME_TOOL_CALL in data or is_block_json_version(data, type="tool_call"):
                return {
                    "message_content": [],
                    "block_list": [{
                        "type": "tool_call",
                        "data": data,
                    }],
                    "iopub_messages": [iopub_msg],
                }
            elif MIME_PLOTLY in data or is_block_json_version(data, type="plotly-json"):
                fig_json = data[MIME_PLOTLY]
                return plotly_response(iopub_msg, fig_json=fig_json)
            elif MIME_TABLE_V1 in data or MIME_TABLE_V2 in data or MIME_TABLE_V3 in data or is_block_json_version(data, type="table"):
                return table_response(iopub_msg, data=data)
            elif MIME_VISUAL in data or is_block_json_version(data, type="visual"):
                return visual_response(iopub_msg, data=data)
            elif MIME_SEARCH_RESULT in data or MIME_SEARCH_RESULT_LIST in data or is_block_json_version(data, type="search_result"):
                return search_result_response(iopub_msg, data=data)
            elif MIME_MARKDOWN in data:
                output = data[MIME_MARKDOWN]
                return text_response(iopub_msg, text=delete_color_control_char(output))
            elif MIME_IMAGE_PNG in data:
                output = data[MIME_IMAGE_PNG]
                output = "data:image/png;base64," + output
                return image_response(iopub_msg, image_url=output)
            elif MIME_IMAGE_JPEG in data:
                output = data[MIME_IMAGE_JPEG]
                output = "data:image/jpeg;base64," + output
                return image_response(iopub_msg, image_url=output)
            elif MIME_HTML in data:
                output = data[MIME_HTML]
                return html_response(iopub_msg, text=output)
            elif MIME_TEXT in data:
                output = data[MIME_TEXT]
                return text_response(iopub_msg, text=delete_color_control_char(output))
            else:
                logger.warning("content type not supported in display_data")
                logger.warning(data)
    elif iopub_msg["msg_type"] == "error":
        if "traceback" in iopub_msg["content"]:
            output = "\n".join(iopub_msg["content"]["traceback"])
            text = delete_color_control_char(output)
            if mode == "debug":
                return text_response(iopub_msg, text=text)
            else:
                return {
                    "message_content": [{"type": "text", "text": text}],
                    "block_list": [],  # No block for error messages
                    "iopub_messages": [iopub_msg],
                }
    return None

def parse_msg_list_to_tool_response(msg_list: list[Optional[dict]], mode: Literal["simple", "full", "debug"]) -> ToolResponse:
    tool_response = {
        "message_content": [],
        "block_list": [],
        "iopub_messages": [],
    }
    for i, msg in enumerate(msg_list):
        logger.debug(f"Processing message {i+1}/{len(msg_list)}: {msg['msg_type'] if msg else 'None'}")
        response = iopub_msg_to_tool_response(msg, mode)
        if response:
            tool_response["message_content"].extend(response.get("message_content", []))
            tool_response["block_list"].extend(response.get("block_list", []))
            tool_response["iopub_messages"].extend(response.get("iopub_messages", []))
            logger.debug(f"\n{content_to_text(response.get('message_content', []))}")
    return tool_response
