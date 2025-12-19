from typing_extensions import Any, Literal, TypedDict, Optional, Union, Annotated, TypeAlias
from pydantic import Field
import re


MIME_MARKDOWN = "text/markdown"
MIME_TEXT = "text/plain"


class TextBlock(TypedDict, total=False):
    type: Literal["text"]
    text: str
    id: Optional[int]


MIME_IMAGE_PNG = "image/png"
MIME_IMAGE_JPEG = "image/jpeg"


class ImageUrl(TypedDict, total=False):
    url: str  # base64, http, or file path


class ImageBlock(TypedDict):
    type: Literal["image_url"]
    image_url: ImageUrl
    id: Optional[int]

BasicBlock = Union[
    TextBlock,
    ImageBlock,
]

MIME_PLOTLY = "application/vnd.plotly.v1+json"


class PlotlyBlock(TypedDict):
    type: Literal["plotly-json"]
    data: dict[Literal["application/vnd.plotly.v1+json"], dict]
    id: Optional[int]


TYPE_TABLE = "table-json"
MIME_TABLE_V1 = "application/vnd.aime.table.v1+json"


class TableDataV1(TypedDict):
    # v1 是通用 dataframe 的渲染
    columns: list[dict[str, Any]]
    datas: list[dict[str, Any]]
    caption: Optional[str]


MIME_TABLE_V2 = "application/vnd.aime.table.v2+json"


class TableDataV2(TypedDict):
    # v2 是带 text2sql 的 dataframe 渲染
    columns: list[dict[str, Any]]
    datas: list[dict[str, Any]]
    caption: Optional[str]
    condition: str
    model_sql: str
    model_condition: str
    chunks_info: str
    meta: str
    row_count: str
    code_count: str
    token: str
    status_code: str
    status_msg: str

MIME_TABLE_V3 = "application/vnd.aime.table.v3+json"

class TableDataV3(TypedDict):
    # v3 是带压缩的 dataframe 渲染
    # 只保留前 50 行数据，超出部分只保留行数信息
    table_id: str  # 前端根据此 id 进行翻页
    columns: list[dict[str, Any]]
    datas: list[dict[str, Any]]
    caption: Optional[str]
    condition: str
    model_sql: str
    model_condition: str
    chunks_info: str
    meta: str
    row_count: str
    code_count: str
    token: str
    status_code: str
    status_msg: str

class TableBlock(TypedDict):
    type: Literal["table-json"]
    data: Union[
        dict[Literal["application/vnd.aime.table.v1+json"], TableDataV1],
        dict[Literal["application/vnd.aime.table.v2+json"], TableDataV2],
        dict[Literal["application/vnd.aime.table.v3+json"], TableDataV3],
    ]
    id: Optional[int]


MIME_HTML = "text/html"


class HtmlBlock(TypedDict):
    type: Literal["html"]
    data: dict[Literal["text/html"], str]  # HTML content
    id: Optional[int]


MIME_JSON = "application/json"


class JsonBlock(TypedDict):
    type: Literal["json"]
    data: dict[Literal["application/json"], dict]
    id: Optional[int]


TYPE_ENV_EVENT = "env_event"
MIME_ENV_EVENT = "application/vnd.env.event.v1+json"


class EnvEvent(TypedDict):
    done: bool
    info: Optional[dict[str, Any]]


class EnvEventBlock(TypedDict):
    type: Literal["env_event"]
    data: dict[Literal["application/vnd.env.event.v1+json"], EnvEvent]


TYPE_SEARCH_RESULT = "search_result"
MIME_SEARCH_RESULT = "application/vnd.search_result.v1+json"
MIME_SEARCH_RESULT_LIST = "application/vnd.search_result_list.v1+json"


class SearchResult(TypedDict):
    title: str
    url: str
    abstract: Optional[str]
    content: Optional[str]
    error: Optional[str]
    result_id: Optional[str]
    publish_time: Optional[str]


class SearchResultBlock(TypedDict):
    type: Literal["search_result"]
    data: dict[Literal["application/vnd.search_result.v1+json"], SearchResult]
    id: Optional[int]


MIME_TOOL_CALL = "application/vnd.aime.tool.call+json"


class ToolCallData(TypedDict):
    call_id: str
    tool_name: str
    tool_args: dict[str, Any]
    tool_id: Optional[str]
    tool_title: Optional[str]
    tool_icon: Optional[str]


class ToolCallBlock(TypedDict):
    type: Literal["tool_call"]
    data: dict[Literal["application/vnd.aime.tool.call+json"], ToolCallData]


TYPE_VISUAL = "visual-json"
MIME_VISUAL = "application/vnd.aime.visual.v1+json"
# from chatkit.widgets import Card, ListView

# VisualData: TypeAlias = Annotated[
#     Card | ListView,
#     Field(discriminator="type"),
# ]
# TODO 集成 openai 的 chatkit.widgets

class VisualDataV1(TypedDict):
    # v1 是通用 visual 的渲染
    type: str
    config: dict[str, Any]
    caption: Optional[str]

class VisualBlock(TypedDict):
    type: Literal["visual-json"]
    data: dict[Literal["application/vnd.aime.visual.v1+json"], VisualDataV1]
    id: Optional[int]
    # embed_id: Optional[str]  # 用于前端定位嵌入位置的 ID


TYPE_DOCUMENT = "document-json"
MIME_DOCUMENT = "application/vnd.aime.document.v1+json"


class DocumentTextBlock(TypedDict):
    id: str
    page_index: int
    bbox: list[int]
    type: Literal["text"]
    text: str
    text_level: Optional[int] # 标题会被归一为 text，并附带 text_level

class DocumentImageBlock(TypedDict):
    id: str
    page_index: int
    bbox: list[int]
    type: Literal["image"]
    image_url: str # 图片路径 or base64
    # 说明与脚注均为字符串列表
    image_captions: Optional[list[str]]
    image_footnotes: Optional[list[str]]

class DocumentPageNumberBlock(TypedDict):
    id: str
    page_index: int
    bbox: list[int]
    type: Literal["page_number"]
    text: str

class DocumentPageFootnoteBlock(TypedDict):
    id: str
    page_index: int
    bbox: list[int]
    type: Literal["page_footnote"]
    text: str

class DocumentListBlock(TypedDict):
    id: str
    page_index: int
    bbox: list[int]
    type: Literal["list"]
    sub_type: str
    list_items: list[str]

# 头/脚/侧栏/引用/音标等文本型块
class DocumentHeaderBlock(TypedDict):
    id: str
    page_index: int
    bbox: list[int]
    type: Literal["header"]
    text: str

class DocumentFooterBlock(TypedDict):
    id: str
    page_index: int
    bbox: list[int]
    type: Literal["footer"]
    text: str

class DocumentAsideTextBlock(TypedDict):
    id: str
    page_index: int
    bbox: list[int]
    type: Literal["aside_text"]
    text: str

class DocumentRefTextBlock(TypedDict):
    id: str
    page_index: int
    bbox: list[int]
    type: Literal["ref_text"]
    text: str

class DocumentPhoneticBlock(TypedDict):
    id: str
    page_index: int
    bbox: list[int]
    type: Literal["phonetic"]
    text: str

# 公式（行间公式统一为 equation + latex）
class DocumentEquationBlock(TypedDict):
    id: str
    page_index: int
    bbox: list[int]
    type: Literal["equation"]
    text: str
    text_format: Literal["latex"]

# 表格，既可能携带 HTML，也可能只有图片路径
class DocumentTableBlock(TypedDict):
    id: str
    page_index: int
    bbox: list[int]
    type: Literal["table"]
    # HTML 内容（如果有）
    table_body: Optional[str]
    # 备选的图片路径
    img_path: Optional[str]
    table_caption: Optional[list[str]]
    table_footnote: Optional[list[str]]

# 代码块
class DocumentCodeBlock(TypedDict):
    id: str
    page_index: int
    bbox: list[int]
    type: Literal["code"]
    sub_type: str
    code_body: Optional[str]
    code_caption: Optional[list[str]]
    guess_lang: Optional[str]

# 页面块，表示整页信息
class DocumentPageBlock(TypedDict):
    id: str
    page_index: int
    bbox: list[int]
    type: Literal["page"]
    file_id: str
    width: int
    height: int

# 书籍块，表示整本书信息
class DocumentBookBlock(TypedDict):
    id: str
    file_id: str
    filename: str
    type: Literal["book"]

DocumentV1Block: TypeAlias = Union[
    DocumentTextBlock,
    DocumentImageBlock,
    DocumentPageNumberBlock,
    DocumentPageFootnoteBlock,
    DocumentListBlock,
    DocumentHeaderBlock,
    DocumentFooterBlock,
    DocumentAsideTextBlock,
    DocumentRefTextBlock,
    DocumentPhoneticBlock,
    DocumentEquationBlock,
    DocumentTableBlock,
    DocumentCodeBlock,
    DocumentPageBlock,
    DocumentBookBlock,
]

class DocumentBlock(TypedDict):
    type: Literal["document-json"]
    data: dict[Literal["application/vnd.aime.document.v1+json"], DocumentV1Block]
    id: Optional[int]
    embed_id: Optional[str]  # 用于前端定位嵌入位置的 ID


Block: TypeAlias = Union[
    BasicBlock,
    PlotlyBlock,
    TableBlock,
    HtmlBlock,
    JsonBlock,
    SearchResultBlock,
    VisualBlock,
    ToolCallBlock,
    EnvEventBlock,
    DocumentBlock,
]


MIME_TOOL_RESPONSE = "application/vnd.aime.tool.response+json"


class ToolResponse(TypedDict):
    message_content: list[dict[str, Any]]
    block_list: list[Block]
    data: Optional[dict[str, Any]]


def is_block_json_version(data: dict[str, Any], type: str="table") -> bool:
    for k in data:
        if type == "table":
            if re.match(r"application/vnd\.aime\.table\.v[0-9]+\+json", k):
                return True
        elif type == "visual":
            if re.match(r"application/vnd\.aime\.visual\.v[0-9]+\+json", k):
                return True
        elif type == "plotly-json":
            if re.match(r"application/vnd\.plotly\.v[0-9]+\+json", k):
                return True
        elif type == "document":
            if re.match(r"application/vnd\.aime\.document\.v[0-9]+\+json", k):
                return True
        elif type == "env_event":
            if re.match(r"application/vnd\.env\.event\.v[0-9]+\+json", k):
                return True
        elif type == "search_result":
            if re.match(r"application/vnd\.search_result(_list)?\.v[0-9]+\+json", k):
                return True
        elif type == "tool_call":
            if re.match(r"application/vnd\.aime\.tool\.call(\.v[0-9]+)?\+json", k):
                return True
        elif type == "tool_response":
            if re.match(r"application/vnd\.aime\.tool\.response(\.v[0-9]+)?\+json", k):
                return True
    return False


def common_mimebundle(
    message_content: list[dict[str, Any]],
    block_list: list[Block],
    data: Optional[dict[str, Any]] = None,
):
    """
    Create a common mimebundle for tool response data

    Args:
        message_content: List of dictionaries containing message content
        block_list: List of Block dictionaries
        data: Additional data dictionary
    Returns:
        A dictionary representing the mimebundle
    """
    return {
        MIME_TOOL_RESPONSE: ToolResponse(
            message_content=message_content,
            block_list=block_list,
            data=data,
        )
    }