from typing import TypedDict, Union, List, NotRequired

# TypedDict 定义不同类型的返回值结构
class TextBlockContent(TypedDict):
    type: str  # BlockType.TEXT, REF_TEXT, PHONETIC, HEADER, FOOTER, PAGE_NUMBER, ASIDE_TEXT, PAGE_FOOTNOTE
    text: str
    page_idx: int
    bbox: NotRequired[List[int]]


class ListBlockContent(TypedDict):
    type: str  # BlockType.LIST
    sub_type: str
    list_items: List[str]
    page_idx: int
    bbox: NotRequired[List[int]]


class TitleBlockContent(TypedDict):
    type: str  # BlockType.TITLE
    text: str
    text_level: NotRequired[int]
    page_idx: int
    bbox: NotRequired[List[int]]


class EquationBlockContent(TypedDict):
    type: str  # BlockType.EQUATION
    text: str
    text_format: str  # 'latex'
    page_idx: int
    bbox: NotRequired[List[int]]


class ImageBlockContent(TypedDict):
    type: str  # BlockType.IMAGE
    img_path: str
    image_caption: List[str]
    image_footnote: List[str]
    page_idx: int
    bbox: NotRequired[List[int]]


class TableBlockContent(TypedDict):
    type: str  # BlockType.TABLE
    img_path: str
    table_caption: List[str]
    table_footnote: List[str]
    table_body: NotRequired[str]  # HTML content
    page_idx: int
    bbox: NotRequired[List[int]]


class CodeBlockContent(TypedDict):
    type: str  # BlockType.CODE
    sub_type: str
    code_body: str
    code_caption: List[str]
    guess_lang: NotRequired[str]
    page_idx: int
    bbox: NotRequired[List[int]]


# 联合类型,表示所有可能的返回值
ParaContent = Union[
    TextBlockContent,
    ListBlockContent,
    TitleBlockContent,
    EquationBlockContent,
    ImageBlockContent,
    TableBlockContent,
    CodeBlockContent
]