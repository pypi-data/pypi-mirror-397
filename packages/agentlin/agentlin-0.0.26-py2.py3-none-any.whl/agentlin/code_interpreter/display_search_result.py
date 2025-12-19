from typing import Iterable, Any

from agentlin.code_interpreter.types import (
    MIME_SEARCH_RESULT,
    MIME_SEARCH_RESULT_LIST,
    SearchResult,
)
from agentlin.code_interpreter.display_mime import MimeDisplayObject, display


REQUIRED_KEYS = ["title", "url"]
OPTIONAL_KEYS = ["abstract", "content", "error", "result_id", "publish_time", "msg_id", "summary"]


def search_result_to_text(search_result: SearchResult) -> str:
    """Convert SearchResult (plus possible extended keys) to a readable text format.

    支持的扩展字段（如存在则输出）：msg_id, summary。
    """
    texts: list[str] = []
    if "title" in search_result:
        texts.append(f"Title: {search_result['title']}")
    if "msg_id" in search_result:
        texts.append(f"msg_id: {search_result['msg_id']}")
    if "result_id" in search_result:
        texts.append(f"result_id: {search_result['result_id']}")
    if "url" in search_result:
        texts.append(f"URL: {search_result['url']}")
    if "publish_time" in search_result:
        texts.append(f"Publish Time: {search_result['publish_time']}")
    if "abstract" in search_result and search_result.get("abstract"):
        texts.append(f"Abstract: {search_result['abstract']}")
    if "error" in search_result and search_result.get("error"):
        texts.append(f"Error: {search_result['error']}")
    if "content" in search_result and search_result.get("content"):
        texts.append(f"Content: {search_result['content']}")
    if "summary" in search_result and search_result.get("summary"):
        texts.append(f"Summary: {search_result['summary']}")
    return "\n".join(texts)


def _normalize_single(data: dict[str, Any], *, idx: int = 0) -> SearchResult:
    """Normalize user-provided dict into a SearchResult structure.

    Missing optional keys are filled with None. An "id" field is always set (if
    absent) using the provided positional index.
    """

    # 复制防止污染外部
    result = dict(data)  # shallow copy

    # 保证基本字段存在
    for k in REQUIRED_KEYS:
        result.setdefault(k, "")

    for k in OPTIONAL_KEYS:
        result.setdefault(k, None)

    # id 规范：若已有 id 且是 int，保留；否则使用传入 idx
    if not isinstance(result.get("id"), int):
        result["id"] = idx

    # 类型注解返回
    return result  # type: ignore


def display_search_result(result: SearchResult, *, auto_id: bool = True):
    """展示单条搜索结果。

    参数:
        result: 单条搜索结果字典或已规范化对象
        auto_id: 若没有 id 是否自动补充 (默认为 True)
    """

    if not isinstance(result, dict):  # 防御性（TypedDict 也是 dict 实例，这里主要为类型清晰）
        result = dict(result)  # type: ignore

    if auto_id and not isinstance(result.get("id"), int):
        result["id"] = 0

    normalized = _normalize_single(result, idx=result.get("id", 0))
    display_obj = MimeDisplayObject(MIME_SEARCH_RESULT, normalized)  # type: ignore[arg-type]
    display(display_obj)


def display_search_results(results: Iterable[SearchResult]):
    """展示多条搜索结果列表。"""

    normalized_list: list[SearchResult] = []
    for idx, item in enumerate(results):
        if not isinstance(item, dict):
            item = dict(item)  # type: ignore
        normalized_list.append(_normalize_single(item, idx=idx))

    data_bundle = {"search_results": normalized_list}
    display_obj = MimeDisplayObject(MIME_SEARCH_RESULT_LIST, data_bundle)  # type: ignore[arg-type]
    display(display_obj)
