from typing import Any, Literal, Union

from agentlin.code_interpreter.data_to_document_json import (
    AiDocument,
    PageBlock,
    TextBlock,
    ImageBlock,
    TableBlock,
    CodeBlock,
    ListBlock,
    EquationBlock,
)


def display_document(
    document: AiDocument,
    modalities: set[Literal["text", "image"]] = {"text", "image"},
    start_page_id: int = 0,
    end_page_id: int = -1,
) -> None:
    document.display(modalities=modalities, start_page_id=start_page_id, end_page_id=end_page_id)


def display_document_page(
    page: PageBlock,
    modalities: set[Literal["text", "image"]] = {"text", "image"},
    start_block_id: int = 0,
    end_block_id: int = -1,
) -> None:
    page.display(modalities=modalities, start_block_id=start_block_id, end_block_id=end_block_id)


def display_document_block(
    block: Union[TextBlock, ImageBlock, TableBlock, CodeBlock, ListBlock, EquationBlock],
    modalities: set[Literal["text", "image"]] = {"text", "image"},
) -> None:
    block.display(modalities=modalities)
