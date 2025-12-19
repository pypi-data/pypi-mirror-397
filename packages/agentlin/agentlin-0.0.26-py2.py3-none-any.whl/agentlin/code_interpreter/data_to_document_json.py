from __future__ import annotations

import os
import re
from typing import Annotated, Any, Dict, IO, List, Optional, TypeAlias, Union, Literal
import json
from pathlib import Path

from pydantic import BaseModel, Field, TypeAdapter
from PIL import Image

from xlin import load_json
from mineru.data.data_reader_writer import DataWriter, FileBasedDataWriter
from mineru.utils.enum_class import BlockType, ContentType, ImageType
from mineru.backend.vlm.vlm_analyze import MinerUClient, ModelSingleton
from mineru.backend.vlm.model_output_to_middle_json import result_to_middle_json
from mineru.backend.vlm.vlm_middle_json_mkcontent import merge_para_with_text, get_title_level, make_blocks_to_content_list
from mineru.cli.common import read_fn, prepare_env
from mineru.utils.pdf_image_tools import get_crop_img, load_images_from_pdf

from agentlin.code_interpreter.types import (
    TYPE_DOCUMENT,
    MIME_DOCUMENT,
    DocumentV1Block,
    DocumentBookBlock,
    DocumentPageBlock,
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
    DocumentBlock,
    common_mimebundle,
)
from agentlin.core.multimodal import image_to_base64, text_to_image
from agentlin.tools.stateful_document.mineru.types import ParaContent


class ImageURL(BaseModel):
    url: str = Field(description="本地文件路径、公共 URL 或 Base64 编码的图像字符串。")


class TextOutputBlock(BaseModel):
    type: Literal["text"] = Field(default="text")
    text: str
    id: Optional[Union[int, str]] = None


class ImageOutputBlock(BaseModel):
    type: Literal["image_url"] = Field(default="image_url")
    image_url: ImageURL
    id: Optional[Union[int, str]] = None


OutputBlock = Union[TextOutputBlock, ImageOutputBlock]


class BaseBlockModel(BaseModel):
    id: str
    file_id: str

    def to_document_json(self) -> DocumentV1Block:
        raise NotImplementedError

    def __str__(self) -> str:
        from agentlin.code_interpreter.display_mime import display
        display(self)
        return ""

    def _repr_mimebundle_(self, include=None, exclude=None) -> dict[str, Any]:
        """
        Return MIME bundle for Jupyter display

        Returns:
            Dict containing the custom MIME type and chart JSON data
        """
        return {
            MIME_DOCUMENT: self.model_dump()
        }

class BaseDataBlockModel(BaseBlockModel):
    bbox: List[int | float]
    page_idx: int
    block_idx: int


class TextBlockModel(BaseDataBlockModel):
    type: Literal["text"] = "text"
    text: str
    text_level: Optional[int] = None

    def to_document_json(self) -> DocumentTextBlock:
        return DocumentTextBlock(
            id=self.id,
            page_index=self.page_idx,
            bbox=self.bbox,
            type=self.type,
            text=self.text,
            text_level=self.text_level,
        )


class ImageBlockModel(BaseDataBlockModel):
    type: Literal["image"] = "image"
    img_path: str
    image_caption: List[str] = []
    image_footnote: List[str] = []

    def to_document_json(self) -> DocumentImageBlock:
        return DocumentImageBlock(
            id=self.id,
            page_index=self.page_idx,
            bbox=self.bbox,
            type=self.type,
            image_url=self.img_path,
            captions=self.image_caption,
            footnotes=self.image_footnote,
        )


class TableBlockModel(BaseDataBlockModel):
    type: Literal["table"] = "table"
    img_path: str
    table_caption: List[str] = []
    table_footnote: List[str] = []
    table_body: Optional[str] = None  # HTML content

    def to_document_json(self) -> DocumentTableBlock:
        return DocumentTableBlock(
            id=self.id,
            page_index=self.page_idx,
            bbox=self.bbox,
            type=self.type,
            table_body=self.table_body,
            img_path=self.img_path,
            table_caption=self.table_caption if self.table_caption else None,
            table_footnote=self.table_footnote if self.table_footnote else None,
        )


class CodeBlockModel(BaseDataBlockModel):
    type: Literal["code"] = "code"
    sub_type: str
    code_body: str
    code_caption: List[str] = []
    guess_lang: Optional[str] = None

    def to_document_json(self) -> DocumentCodeBlock:
        return DocumentCodeBlock(
            id=self.id,
            page_index=self.page_idx,
            bbox=self.bbox,
            type=self.type,
            sub_type=self.sub_type,
            code_body=self.code_body if self.code_body else None,
            code_caption=self.code_caption if self.code_caption else None,
            guess_lang=self.guess_lang,
        )


class ListBlockModel(BaseDataBlockModel):
    type: Literal["list"] = "list"
    sub_type: Optional[str] = None  # sub_type in ParaContent
    list_items: List[str] = []  # list_items in ParaContent

    def to_document_json(self) -> DocumentListBlock:
        return DocumentListBlock(
            id=self.id,
            page_index=self.page_idx,
            bbox=self.bbox,
            type=self.type,
            sub_type=self.sub_type or "",
            list_items=self.list_items,
        )


class EquationBlockModel(BaseDataBlockModel):
    type: Literal["equation"] = "equation"
    text: str  # LaTeX text
    text_format: str = "latex"  # text_format in ParaContent

    def to_document_json(self) -> DocumentEquationBlock:
        return DocumentEquationBlock(
            id=self.id,
            page_index=self.page_idx,
            bbox=self.bbox,
            type=self.type,
            text=self.text,
            text_format=self.text_format,
        )


class PageBlockModel(BaseDataBlockModel):
    type: Literal["page"] = "page"
    width: int
    height: int
    total_pages: int
    blocks: List[BaseDataBlockModel]

    def to_document_json(self) -> DocumentPageBlock:
        return DocumentPageBlock(
            id=self.id,
            page_index=self.page_idx,
            bbox=self.bbox,
            type=self.type,
            file_id=self.file_id,
            width=self.width,
            height=self.height,
        )


DataBlockModelType: TypeAlias = Union[
    TextBlockModel,
    ImageBlockModel,
    TableBlockModel,
    CodeBlockModel,
    ListBlockModel,
    EquationBlockModel,
    PageBlockModel,
]

DataBlockModel = TypeAdapter(
    Annotated[
        DataBlockModelType,
        Field(discriminator="type"),
    ]
)


class DocumentBlockModel(BaseBlockModel):
    """Document 的 Block Model"""
    type: Literal["document"] = "document"
    filename: str
    pages: List[PageBlockModel]

    def to_document_json(self) -> dict:
        """Convert to document JSON format"""
        return DocumentBookBlock(
            id=self.id,
            file_id=self.file_id,
            filename=self.filename,
            type="book",
        )


BlockModelType: TypeAlias = Union[
    DataBlockModelType,
    DocumentBlockModel,
]


BlockModel = TypeAdapter(
    Annotated[
        BlockModelType,
        Field(discriminator="type"),
    ]
)


class BaseBlock:
    def __init__(self, model: BlockModelType):
        self._model = model

    @property
    def id(self) -> str:
        return self._model.id

    @property
    def type(self) -> str:
        return self._model.type

    def to_output_block(
        self,
        modalities: set[Literal["text", "image"]] = {"text"},
        *args,
        **kwargs,
    ) -> List[OutputBlock]:
        raise NotImplementedError

    def _repr_mimebundle_(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.setdefault("modalities", {"text", "image"})
        modalities: set[Literal["text", "image"]] = kwargs["modalities"]
        output_blocks = self.to_output_block(modalities=modalities)
        message_content = [block.model_dump(exclude_none=True) for block in output_blocks]
        block_list = [
            DocumentBlock(
                type=TYPE_DOCUMENT,
                data={
                    MIME_DOCUMENT: self._model.to_document_json(),
                }
            )
        ]
        return common_mimebundle(
            message_content=message_content,
            block_list=block_list,
            data=None,
        )

    def display(
        self,
        modalities: set[Literal["text", "image"]] = {"text"},
        *args,
        **kwargs,
    ) -> None:
        from agentlin.code_interpreter.display_mime import display, RawDisplayObject

        output_blocks = self.to_output_block(modalities=modalities, *args, **kwargs)
        message_content = [block.model_dump(exclude_none=True) for block in output_blocks]
        block_list = [
            DocumentBlock(
                type=TYPE_DOCUMENT,
                data={
                    MIME_DOCUMENT: self._model.to_document_json(),
                }
            )
        ]
        mimebundle = common_mimebundle(
            message_content=message_content,
            block_list=block_list,
            data=None,
        )
        display(RawDisplayObject(mimebundle))

class BaseDataBlock(BaseBlock):
    def __init__(self, model: DataBlockModelType, page_image: Optional[Image.Image] = None):
        super().__init__(model)
        self._model = model
        self._page_image = page_image

    def to_text(self) -> str:
        raise NotImplementedError

    def to_image(self) -> Image.Image:
        raise NotImplementedError

    def to_text_block(self) -> TextOutputBlock:
        return TextOutputBlock(text=self.to_text())

    def to_image_block(self) -> ImageOutputBlock:
        image = self.to_image()
        image_base64 = image_to_base64(image)
        return ImageOutputBlock(image_url=ImageURL(url=image_base64))

    def to_output_block(self, modalities: set[Literal["text", "image"]] = {"text"}) -> List[OutputBlock]:
        """
        Convert to output blocks based on specified modalities.
        优先级别：text > image
        """
        output: List[OutputBlock] = []
        if "text" in modalities:
            output.append(self.to_text_block())
        elif "image" in modalities:
            output.append(self.to_image_block())
        return output


class TextBlock(BaseDataBlock):
    def __init__(self, model: TextBlockModel, page_image: Optional[Image.Image] = None):
        super().__init__(model, page_image)
        self._model: TextBlockModel = model

    def to_text(self) -> str:
        return self._model.text

    def to_image(self) -> Image.Image:
        if self._page_image and self._model.bbox:
            try:
                real_bbox = [
                    self._model.bbox[0] / 1000 * self._page_image.width,
                    self._model.bbox[1] / 1000 * self._page_image.height,
                    self._model.bbox[2] / 1000 * self._page_image.width,
                    self._model.bbox[3] / 1000 * self._page_image.height,
                ]
                return get_crop_img(tuple(real_bbox), self._page_image, scale=1)
            except Exception:
                pass
        # 回退方案：生成文字图像
        return text_to_image(self._model.text)


class ImageBlock(BaseDataBlock):
    def __init__(self, model: ImageBlockModel, page_image: Optional[Image.Image] = None):
        super().__init__(model, page_image)
        self._model: ImageBlockModel = model

    def to_text(self) -> str:
        caption = " ".join(self._model.image_caption) if self._model.image_caption else ""
        return f"[{caption}]({self._model.img_path})"

    def to_image(self) -> Image.Image:
        # 优先使用已解析的图像路径
        if self._model.img_path:
            try:
                return Image.open(self._model.img_path).convert("RGB")
            except Exception:
                pass
        # 回退到页面裁剪
        if self._page_image and self._model.bbox:
            try:
                real_bbox = [
                    self._model.bbox[0] / 1000 * self._page_image.width,
                    self._model.bbox[1] / 1000 * self._page_image.height,
                    self._model.bbox[2] / 1000 * self._page_image.width,
                    self._model.bbox[3] / 1000 * self._page_image.height,
                ]
                return get_crop_img(tuple(real_bbox), self._page_image, scale=1)
            except Exception:
                pass
        return Image.new("RGB", (150, 150), color="blue")

    def to_output_block(self, modalities: set[Literal["text", "image"]] = {"text"}) -> List[OutputBlock]:
        output: List[OutputBlock] = []
        if "text" in modalities and "image" in modalities:
            if self._model.image_caption:
                output.append(TextOutputBlock(text="Image Caption: " + " ".join(self._model.image_caption)))
            output.append(self.to_image_block())
            if self._model.image_footnote:
                output.append(TextOutputBlock(text="Image Footnote: " + " ".join(self._model.image_footnote)))
        elif "text" in modalities:
            output.append(self.to_text_block())
        elif "image" in modalities:
            output.append(self.to_image_block())
        return output


class TableBlock(BaseDataBlock):
    def __init__(self, model: TableBlockModel, page_image: Optional[Image.Image] = None):
        super().__init__(model, page_image)
        self._model: TableBlockModel = model

    def to_text(self) -> str:
        parts: List[str] = []
        if self._model.table_caption:
            parts.append("Table Caption: " + " ".join(self._model.table_caption))
        if self._model.table_body:
            parts.append(self._model.table_body)
        if self._model.table_footnote:
            parts.append("Table Footnote: " + " ".join(self._model.table_footnote))
        return "\n".join(parts) if parts else "[Table]"

    def to_image(self) -> Image.Image:
        if self._model.img_path:
            try:
                return Image.open(self._model.img_path).convert("RGB")
            except Exception:
                pass
        if self._page_image and self._model.bbox:
            try:
                real_bbox = [
                    self._model.bbox[0] / 1000 * self._page_image.width,
                    self._model.bbox[1] / 1000 * self._page_image.height,
                    self._model.bbox[2] / 1000 * self._page_image.width,
                    self._model.bbox[3] / 1000 * self._page_image.height,
                ]
                return get_crop_img(tuple(real_bbox), self._page_image, scale=1)
            except Exception:
                pass
        return Image.new("RGB", (200, 100), color="lightgray")

    def to_output_block(self, modalities: set[Literal["text", "image"]] = {"text"}) -> List[OutputBlock]:
        output: List[OutputBlock] = []
        if "text" in modalities and "image" in modalities:
            if self._model.table_caption:
                output.append(TextOutputBlock(text="Table Caption: " + " ".join(self._model.table_caption)))
            output.append(self.to_image_block())
            if self._model.table_footnote:
                output.append(TextOutputBlock(text="Table Footnote: " + " ".join(self._model.table_footnote)))
        elif "text" in modalities:
            output.append(self.to_text_block())
        elif "image" in modalities:
            output.append(self.to_image_block())
        return output


class CodeBlock(BaseDataBlock):
    def __init__(self, model: CodeBlockModel, page_image: Optional[Image.Image] = None):
        super().__init__(model, page_image)
        self._model: CodeBlockModel = model

    def to_text(self) -> str:
        parts: List[str] = []
        if self._model.code_caption:
            parts.append("Code Caption: " + " ".join(self._model.code_caption))
        parts.append(self._model.code_body)
        return "\n".join(parts)

    def to_image(self) -> Image.Image:
        if self._page_image and self._model.bbox:
            try:
                real_bbox = [
                    self._model.bbox[0] / 1000 * self._page_image.width,
                    self._model.bbox[1] / 1000 * self._page_image.height,
                    self._model.bbox[2] / 1000 * self._page_image.width,
                    self._model.bbox[3] / 1000 * self._page_image.height,
                ]
                return get_crop_img(tuple(real_bbox), self._page_image, scale=1)
            except Exception:
                pass
        return Image.new("RGB", (200, 100), color="lightgray")


class ListBlock(BaseDataBlock):
    def __init__(self, model: ListBlockModel, page_image: Optional[Image.Image] = None):
        super().__init__(model, page_image)
        self._model: ListBlockModel = model

    def to_text(self) -> str:
        return "\n".join(self._model.list_items)

    def to_image(self) -> Image.Image:
        if self._page_image and self._model.bbox:
            try:
                real_bbox = [
                    self._model.bbox[0] / 1000 * self._page_image.width,
                    self._model.bbox[1] / 1000 * self._page_image.height,
                    self._model.bbox[2] / 1000 * self._page_image.width,
                    self._model.bbox[3] / 1000 * self._page_image.height,
                ]
                return get_crop_img(tuple(real_bbox), self._page_image, scale=1)
            except Exception:
                pass
        return text_to_image(self.to_text())


class EquationBlock(BaseDataBlock):
    def __init__(self, model: EquationBlockModel, page_image: Optional[Image.Image] = None):
        super().__init__(model, page_image)
        self._model: EquationBlockModel = model

    def to_text(self) -> str:
        if self._model.text_format == "latex":
            return f"$${self._model.text}$$"
        return self._model.text

    def to_image(self) -> Image.Image:
        if self._page_image and self._model.bbox:
            try:
                real_bbox = [
                    self._model.bbox[0] / 1000 * self._page_image.width,
                    self._model.bbox[1] / 1000 * self._page_image.height,
                    self._model.bbox[2] / 1000 * self._page_image.width,
                    self._model.bbox[3] / 1000 * self._page_image.height,
                ]
                return get_crop_img(tuple(real_bbox), self._page_image, scale=1)
            except Exception:
                pass
        return text_to_image(self.to_text())

    def _repr_latex_(self) -> str:
        if self._model.text_format == "latex":
            return f"$${self._model.text}$$"
        return self._model.text


def _create_block_instance(model: DataBlockModelType, page_image: Optional[Image.Image] = None) -> BaseBlock:
    if isinstance(model, TextBlockModel):
        return TextBlock(model, page_image)
    if isinstance(model, ImageBlockModel):
        return ImageBlock(model, page_image)
    if isinstance(model, TableBlockModel):
        return TableBlock(model, page_image)
    if isinstance(model, CodeBlockModel):
        return CodeBlock(model, page_image)
    if isinstance(model, ListBlockModel):
        return ListBlock(model, page_image)
    if isinstance(model, EquationBlockModel):
        return EquationBlock(model, page_image)
    if isinstance(model, PageBlockModel):
        return PageBlock(model, page_image)
    raise ValueError(f"Unknown block model type: {type(model)}")


class PageBlock(BaseBlock):
    def __init__(self, model: PageBlockModel, page_image: Optional[Image.Image] = None):
        # 为 Page 创建一个 PageBlockModel
        super().__init__(model)
        self._model: PageBlockModel = model
        self._page_image = page_image
        self.blocks: List[BaseBlock] = [_create_block_instance(b, page_image) for b in model.blocks]

    def __len__(self) -> int:
        return len(self.blocks)

    @property
    def page_idx(self) -> int:
        return self._model.page_idx

    @property
    def total_pages(self) -> int:
        return self._model.total_pages

    @property
    def text_blocks(self) -> List[TextBlock]:
        return [b for b in self.blocks if isinstance(b, TextBlock)]
    @property
    def tables(self) -> List[TableBlock]:
        return [b for b in self.blocks if isinstance(b, TableBlock)]
    @property
    def images(self) -> List[ImageBlock]:
        return [b for b in self.blocks if isinstance(b, ImageBlock)]
    @property
    def code_blocks(self) -> List[CodeBlock]:
        return [b for b in self.blocks if isinstance(b, CodeBlock)]
    @property
    def equations(self) -> List[EquationBlock]:
        return [b for b in self.blocks if isinstance(b, EquationBlock)]

    def to_output_block(
        self,
        modalities: set[Literal["text", "image"]] = {"text", "image"},
        start_block_id: int = 0,
        end_block_id: int = -1,
    ) -> List[OutputBlock]:
        """支持两种模式：BaseBlock 的 convert_to 模式和原有的 view 模式"""
        output: List[OutputBlock] = []
        output.append(TextOutputBlock(text=f"<Page>\nPage Index {self.page_idx}, Total Pages: {self.total_pages}\n"))
        if not self.blocks:
            output.append(TextOutputBlock(text="[No blocks in this page]\n</Page>"))
            return output
        start = start_block_id
        end = end_block_id
        if start < 0:
            start = 0
        if end == -1 or end > len(self.blocks):
            end = len(self.blocks)

        display_num_blocks = end - start

        if start <= 0 and (end == -1 or end >= len(self.blocks)):
            if modalities == {"image"}:
                # 展示全部块，且只允许展示图像时，优先展示整页图像
                if self._page_image:
                    output.append(
                        ImageOutputBlock(
                            image_url=ImageURL(url=image_to_base64(self._page_image)),
                        )
                    )
                    output.append(TextOutputBlock(text=f"</Page>"))
                    return output

        # 只展示部分 Block 时,按顺序展示各个 Block
        selected_blocks = self.blocks[start:end]

        for block in selected_blocks:
            if len(selected_blocks) < len(self.blocks):
                output.append(TextOutputBlock(text=f"<Block>\nBlock ID: {block.id}\n"))
            if isinstance(block, (TextBlock, CodeBlock, ListBlock, EquationBlock)):
                # 要么展示文本，要么展示图像。且优先展示文本。
                if "text" in modalities:
                    output.extend(block.to_output_block(modalities={"text"}))
                elif "image" in modalities:
                    output.extend(block.to_output_block(modalities={"image"}))
            elif isinstance(block, TableBlock):
                # 优先展示图像，其次文本
                if "image" in modalities:
                    output.extend(block.to_output_block(modalities={"image"}))
                elif "text" in modalities:
                    output.extend(block.to_output_block(modalities={"text"}))
            elif isinstance(block, ImageBlock):
                if "image" in modalities:
                    output.extend(block.to_output_block(modalities={"image"}))
                elif "text" in modalities:
                    output.extend(block.to_output_block(modalities={"text"}))
            else:
                # 其他类型，默认文本展示
                output.extend(block.to_output_block(modalities={"text"}))
            if len(selected_blocks) < len(self.blocks):
                output.append(TextOutputBlock(text=f"</Block>"))
        output.append(TextOutputBlock(text=f"</Page>"))

        return output

    def display(
        self,
        modalities: set[Literal["text", "image"]] = {"text", "image"},
        start_block_id: int = 0,
        end_block_id: int = -1,
    ) -> None:
        super().display(
            modalities=modalities,
            start_block_id=start_block_id,
            end_block_id=end_block_id,
        )


class AiDocument(BaseBlock):

    def __init__(
        self,
        file_id: str,
        output_dir: Optional[str] = None,
        display_page_limit: int = 10,
        mineru_server_url: Optional[str] = None,
    ):
        self._file_id = Path(file_id)
        self.display_page_limit = display_page_limit
        if not output_dir:
            output_dir = os.getenv("DOCUMENT_OUTPUT_DIR", str(self._file_id.parent))
        output_image_dir, output_md_dir = prepare_env(output_dir, self._file_id.stem, "auto")
        self.output_dir = Path(output_dir)
        self.output_md_dir = Path(output_md_dir)
        self.output_image_dir = Path(output_image_dir)
        self.output_middle_json_path = self.output_md_dir / f"{self._file_id.stem}_middle.json"
        if not mineru_server_url:
            mineru_server_url = os.getenv("MINERU_SERVER_URL", None)

        # 临时创建一个占位 model，会在 load 后更新
        placeholder_model = DocumentBlockModel(
            id=f"file://{self._file_id.absolute()}",
            file_id=f"file://{self._file_id.absolute()}",
            filename=self._file_id.name,
            pages=[],
        )
        super().__init__(placeholder_model)
        self._model: DocumentBlockModel = placeholder_model
        self._page_images: Dict[int, Image.Image] = {}  # 存储页面图像,key为page_idx
        self._pages: List[PageBlock] = []
        self._blocks: List[BaseBlock] = []

        self.load(server_url=mineru_server_url)

    @property
    def file_id(self) -> str:
        return f"file://{self._file_id.absolute()}"

    @property
    def pages(self) -> List[PageBlock]:
        if len(self._pages) == len(self._model.pages):
            return self._pages
        pages = self._model.pages
        self._pages = [PageBlock(p, self._page_images.get(p.page_idx)) for p in pages]
        return self._pages

    @property
    def blocks(self) -> List[BaseBlock]:
        if self._blocks:
            return self._blocks
        all_blocks: List[BaseBlock] = []
        for page in self.pages:
            all_blocks.extend(page.blocks)
        self._blocks = all_blocks
        return self._blocks

    def load(
        self,
        output_image_dir: Optional[str] = None,
        predictor: MinerUClient | None = None,
        backend: str = "vllm-engine",
        model_path: str | None = None,
        server_url: str | None = None,
        middle_json_path: Optional[str] = None,
        **kwargs,
    ):
        """调用 MinerU VLM 后端，获取 middle.json 并构建 DocBlock 结构。"""
        if not isinstance(self._file_id, str) and not isinstance(self._file_id, os.PathLike):
            raise ValueError("DocumentReader currently only supports file-path input for VLM backend.")

        pdf_bytes = read_fn(self._file_id)

        # 加载页面图像用于后续裁剪
        images_list, pdf_doc = load_images_from_pdf(pdf_bytes, image_type=ImageType.PIL)
        # print(len(images_list), "images", len(pdf_doc), "pages loaded from pdf")
        images_pil_list = [image_dict["img_pil"] for image_dict in images_list]
        # 存储页面图像,key为页面索引
        for idx, image_dict in enumerate(images_list):
            if "img_pil" in image_dict:
                self._page_images[idx] = image_dict["img_pil"]
        # print(self.output_middle_json_path, self.output_middle_json_path.exists())
        if middle_json_path:
            middle_json = load_json(middle_json_path)
        elif self.output_middle_json_path.exists():
            middle_json = load_json(self.output_middle_json_path)
        else:
            if not predictor:
                predictor = ModelSingleton().get_model(backend, model_path, server_url, **kwargs)
            results = predictor.batch_two_step_extract(images=images_pil_list)
            # infer_time = round(time.time() - infer_start, 2)
            # logger.info(f"infer finished, cost: {infer_time}, speed: {round(len(results)/infer_time, 3)} page/s")

            if not output_image_dir:
                image_writer = FileBasedDataWriter(self.output_image_dir)
            else:
                image_writer = FileBasedDataWriter(Path(output_image_dir))
            middle_json = result_to_middle_json(results, images_list, pdf_doc, image_writer)
        self.load_from_middle_json(middle_json)

    def load_from_middle_json(self, middle_json: Dict[str, Any]):
        """直接从 middle.json 构建 DocumentModel。"""
        img_buket_path = self.output_image_dir.name
        pdf_info_list = middle_json.get("pdf_info", [])

        # 基于 middle.json 的 pdf_info 构建内部模型
        for page_info in pdf_info_list:
            paras_of_layout = page_info.get('para_blocks') or []
            paras_of_discarded = page_info.get('discarded_blocks') or []
            page_idx = int(page_info.get("page_idx", 0))
            page_size = page_info.get("page_size", [1000, 1000])
            if not paras_of_layout:
                continue
            width, height = page_size[0], page_size[1]
            page = PageBlockModel(
                id=f"file://{self._file_id.absolute()}?page_idx={page_idx}",
                file_id=f"file://{self._file_id.absolute()}",
                bbox=[0, 0, width, height],
                page_idx=page_idx,
                block_idx=-1,
                width=width,
                height=height,
                total_pages=-1,  # 暂时不设置总页数
                blocks=[],
            )
            self._model.pages.append(page)
            # para_blocks = (page_info.get("para_blocks") or []) + (page_info.get("discarded_blocks") or [])
            para_blocks = paras_of_layout + paras_of_discarded
            block_idx = 0
            for para_block in para_blocks:
                para_content: ParaContent = make_blocks_to_content_list(para_block, img_buket_path, page_idx, page_size)

                para_type = para_content.get("type")
                bbox = para_content.get("bbox") or [0, 0, width, height]
                block_idx = block_idx + 1

                base_kwargs = {
                    "id": f"file://{self._file_id.absolute()}?page_idx={page_idx}&block_idx={block_idx}&type={para_type}",
                    "file_id": f"file://{self._file_id.absolute()}",
                    "bbox": bbox,
                    "page_idx": page_idx,
                    "block_idx": block_idx,
                }

                # 使用 ParaContent 的结构化数据
                if para_type in [
                    BlockType.TEXT, BlockType.REF_TEXT, BlockType.PHONETIC, BlockType.HEADER, BlockType.FOOTER,
                    BlockType.PAGE_NUMBER, BlockType.ASIDE_TEXT, BlockType.PAGE_FOOTNOTE,
                ]:
                    page.blocks.append(TextBlockModel(
                        text=para_content.get("text", ""),
                        **base_kwargs,
                    ))
                elif para_type == BlockType.TITLE:  # TitleBlockContent
                    page.blocks.append(TextBlockModel(
                        text=para_content.get("text", ""),
                        text_level=para_content.get("text_level"),
                        **base_kwargs,
                    ))
                elif para_type == BlockType.INTERLINE_EQUATION:  # EquationBlockContent
                    page.blocks.append(EquationBlockModel(
                        text=para_content.get("text", ""),
                        text_format=para_content.get("text_format", "latex"),
                        **base_kwargs,
                    ))
                elif para_type == BlockType.LIST:  # ListBlockContent
                    page.blocks.append(ListBlockModel(
                        sub_type=para_content.get("sub_type"),
                        list_items=para_content.get("list_items", []),
                        **base_kwargs,
                    ))
                elif para_type == BlockType.IMAGE:  # ImageBlockContent
                    # print("Processing image block:", para_content)
                    img_path = para_content.get("img_path", "")
                    if img_path:
                        if img_path.startswith(img_buket_path):
                            img_path = str(self.output_md_dir / img_path)
                        else:
                            img_path = str(self.output_image_dir / img_path)
                    page.blocks.append(ImageBlockModel(
                        img_path=img_path,
                        image_caption=para_content.get("image_caption", []),
                        image_footnote=para_content.get("image_footnote", []),
                        **base_kwargs,
                    ))
                elif para_type == BlockType.TABLE:  # TableBlockContent
                    # print("Processing table block:", para_content)
                    img_path = para_content.get("img_path", "")
                    if img_path:
                        if img_path.startswith(img_buket_path):
                            img_path = str(self.output_md_dir / img_path)
                        else:
                            img_path = str(self.output_image_dir / img_path)
                    page.blocks.append(TableBlockModel(
                        img_path=img_path,
                        table_caption=para_content.get("table_caption", []),
                        table_footnote=para_content.get("table_footnote", []),
                        table_body=para_content.get("table_body"),
                        **base_kwargs,
                    ))
                elif para_type == BlockType.CODE:  # CodeBlockContent
                    page.blocks.append(CodeBlockModel(
                        sub_type=para_content.get("sub_type", ""),
                        code_body=para_content.get("code_body", ""),
                        guess_lang=para_content.get("guess_lang"),
                        code_caption=para_content.get("code_caption", []),
                        **base_kwargs,
                    ))
                else:
                    # 未覆盖类型：尝试从 para_content 提取文本
                    text = para_content.get("text", "")
                    if not text:
                        # 回退到原始解析
                        text = merge_para_with_text(para_block)
                    page.blocks.append(TextBlockModel(
                        text=str(text),
                        **base_kwargs,
                    ))
        for page in self._model.pages:
            page.total_pages = len(self._model.pages)

    def to_output_block(
        self,
        modalities: set[Literal["text", "image"]] = {"text", "image"},
        start_page_id: int = 0,
        end_page_id: int = -1,
    ) -> List[OutputBlock]:
        output: List[OutputBlock] = []
        if not self.pages:
            output.append(TextOutputBlock(text=f"<Document>\n{self.file_id}\nTotal Pages: {len(self.pages)}\nNo pages available.\n</Document>"))
            return output
        output.append(TextOutputBlock(text=f"<Document>\n{self.file_id}\nTotal Pages: {len(self.pages)}"))
        if end_page_id == -1 or end_page_id > len(self.pages):
            end_page_id = len(self.pages)
        if start_page_id < 0:
            start_page_id = 0
        display_page_num = end_page_id - start_page_id
        if display_page_num > self.display_page_limit:
            end_page_id = start_page_id + self.display_page_limit
            output.append(TextOutputBlock(text=f"<Warning> You are trying to display {display_page_num} pages, which exceeds the page limit ({self.display_page_limit}) and may be slow. Displaying only {self.display_page_limit} pages. </Warning>"))
        pages_to_display = self.pages[start_page_id:end_page_id]
        for page in pages_to_display:
            page_output = page.to_output_block(
                modalities=modalities,
            )
            output.extend(page_output)
        output.append(TextOutputBlock(text=f"</Document>"))
        return output

    def display(
        self,
        modalities: set[Literal["text", "image"]] = {"text", "image"},
        start_page_id: int = 0,
        end_page_id: int = -1,
    ) -> None:
        super().display(
            modalities=modalities,
            start_page_id=start_page_id,
            end_page_id=end_page_id,
        )

    def grep(
        self,
        pattern: str,
        case_sensitive: bool = False,
        is_regex: bool = True,
        context_lines: int = 0,
    ) -> None:
        """
        Search for a pattern across all blocks and print matching block IDs with content.

        Args:
            pattern: The search pattern (regex by default, or plain text if is_regex=False)
            case_sensitive: Whether the search should be case-sensitive (default: False)
            is_regex: Whether to treat pattern as regex (default: True)
            context_lines: Number of lines to show before and after match (default: 0)

        Example usage:
        ```python
        # Basic search (regex, case-insensitive)
        doc.grep("pattern")

        # Plain text search
        doc.grep("exact text", is_regex=False)

        # Case-sensitive search
        doc.grep("Pattern", case_sensitive=True)

        # With context lines
        doc.grep("error", context_lines=2)

        # Complex regex
        doc.grep(r"\b[A-Z]{3,}\b")  # Find words with 3+ uppercase letters
        ```
        """
        flags = 0 if case_sensitive else re.IGNORECASE

        if is_regex:
            try:
                regex = re.compile(pattern, flags)
            except re.error as e:
                print(f"Invalid regex pattern: {e}")
                return
        else:
            # Escape special regex characters for plain text search
            escaped_pattern = re.escape(pattern)
            regex = re.compile(escaped_pattern, flags)

        matches_found = 0

        for page in self.pages:
            for block in page.blocks:
                # Get text content from block
                try:
                    if isinstance(block, (TextBlock, ListBlock, EquationBlock)):
                        text_content = block.to_text()
                    elif isinstance(block, CodeBlock):
                        text_content = block._model.code_body
                    elif isinstance(block, TableBlock):
                        text_content = block._model.table_body or ""
                    elif isinstance(block, ImageBlock):
                        # Search in image captions
                        text_content = " ".join(block._model.image_caption)
                    else:
                        continue

                    if not text_content:
                        continue

                    # Search for matches
                    matches = list(regex.finditer(text_content))

                    if matches:
                        matches_found += len(matches)

                        # Print block header
                        print(f"\n{'='*80}")
                        print(f"Block ID: {block.id}")
                        print(f"Matches: {len(matches)}")
                        print(f"{'-'*80}")

                        if context_lines == 0:
                            # Simple mode: just show the matched content
                            for i, match in enumerate(matches, 1):
                                start, end = match.span()
                                # Show some context around the match
                                context_start = max(0, start - 40)
                                context_end = min(len(text_content), end + 40)

                                prefix = "..." if context_start > 0 else ""
                                suffix = "..." if context_end < len(text_content) else ""

                                matched_text = text_content[context_start:context_end]

                                # Highlight the actual match
                                match_start_in_context = start - context_start
                                match_end_in_context = end - context_start

                                highlighted = (
                                    matched_text[:match_start_in_context] +
                                    f"**{matched_text[match_start_in_context:match_end_in_context]}**" +
                                    matched_text[match_end_in_context:]
                                )

                                print(f"Match {i}: {prefix}{highlighted}{suffix}")
                        else:
                            # Context mode: show lines around matches
                            lines = text_content.split('\n')
                            matched_line_numbers = set()

                            for match in matches:
                                # Find which line the match is on
                                match_pos = match.start()
                                current_pos = 0
                                for line_num, line in enumerate(lines):
                                    if current_pos <= match_pos < current_pos + len(line) + 1:
                                        # Add context lines
                                        for ctx_line in range(
                                            max(0, line_num - context_lines),
                                            min(len(lines), line_num + context_lines + 1)
                                        ):
                                            matched_line_numbers.add(ctx_line)
                                        break
                                    current_pos += len(line) + 1  # +1 for newline

                            # Print lines with line numbers
                            for line_num in sorted(matched_line_numbers):
                                line = lines[line_num]
                                # Highlight matches in this line
                                highlighted_line = regex.sub(lambda m: f"**{m.group()}**", line)
                                print(f"{line_num + 1:4d}: {highlighted_line}")

                except Exception as e:
                    # Skip blocks that can't be processed
                    continue

        # Print summary
        print(f"\n{'='*80}")
        if matches_found == 0:
            print(f"No matches found for pattern: {pattern}")
        else:
            print(f"Total matches found: {matches_found}")
        print(f"{'='*80}\n")
