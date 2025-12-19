import datetime
import os
from pathlib import Path
import uuid
from typing import Optional

from loguru import logger
from agentlin.core.multimodal import _download_to, _is_web_url
from agentlin.tools.validate import ensure_package


class ChunkrParser:
    def __init__(self, cache_dir: Path, high_resolution=True) -> None:
        self.cache_dir = cache_dir / "documents"
        ensure_package("chunkr_ai")
        api_key = os.getenv("CHUNKR_API_KEY")
        if not api_key:
            raise ValueError("CHUNKR_API_KEY is required for ChunkrParser but not set in environment variables.")
        from chunkr_ai import Chunkr
        from chunkr_ai.models import Configuration

        self.chunkr = Chunkr(api_key=api_key)
        self.chunkr.config = Configuration(
            high_resolution=high_resolution,
        )

    async def parse(self, path: str) -> str:
        """Parse document to markdown with Chunkr.

        - ref: <https://docs.chunkr.ai/sdk/data-operations/create#supported-file-types>

        Args:
            md5 (str): md5 of the document.
        """
        task = await self.chunkr.upload(path)

        logger.info("  getting results...")
        markdown = task.markdown()
        return markdown


class PDFParser:
    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir / "documents"
        ensure_package("pymupdf")

    async def parse(self, path: str) -> str:
        """Convert PDF to Markdown format with image extraction and return the processed text."""
        import fitz  # pymupdf

        # Create unique directory with date and ID for images
        unique_id = str(uuid.uuid4())[:8]  # First 8 characters of UUID
        output_dir = self.cache_dir / datetime.datetime.now().strftime("%Y-%m-%d") / f"pdf_images_{unique_id}"
        output_dir.mkdir(parents=True, exist_ok=True)

        doc = fitz.open(path)
        markdown_content = ""

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)

            text = page.get_text()
            markdown_content += f"## Page {page_num + 1}\n\n"
            if text.strip():
                markdown_content += text.strip() + "\n\n"
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n < 5:  # GRAY or RGB
                        img_filename = f"page_{page_num}_img_{img_index}.png"
                        img_path = output_dir / img_filename
                        pix.save(img_path)
                        markdown_content += f"![Image]({img_path})\n\n"
                    pix = None
                except Exception as img_e:
                    logger.warning(f"Failed to extract image {img_index} from page {page_num}: {img_e}")
                    continue

        doc.close()
        return markdown_content.strip()


async def document_qa(
    document_path: str,
    question: str,
    *,
    api_key: str,
    base_url: str,
    model: str,
    cache_dir: Path,
    text_limit: int = 100_000,
) -> str:
    """Parse a document to markdown and answer a question or give a summary.

    - Supported parsers:
      - Chunkr (if CHUNKR_API_KEY available)
      - PyMuPDF (PDF only)

    Args:
        document_path: Local path or URL to a document.
        question: Optional question to answer based on the document. If None, return a summary.
        text_limit: Max characters to keep from parsed markdown (default 100_000).
        model, api_key, base_url: Optional OpenAI settings (fallback to env OPENAI_MODEL/OPENAI_API_KEY/OPENAI_BASE_URL).

    Returns:
        str: Model answer or summary.
    """
    # Resolve local path (download if URL)
    local_path = document_path
    if _is_web_url(document_path):
        # try to keep extension, best-effort
        from urllib.parse import urlparse

        parsed = urlparse(document_path)
        ext = Path(parsed.path).suffix or ""
        dst = cache_dir / "downloads" / (uuid.uuid4().hex[:8] + ext)
        local_path = str(await _download_to(document_path, dst))

    # Pick parser
    use_chunkr = os.getenv("CHUNKR_API_KEY") is not None
    ext = Path(local_path).suffix.lower()

    if use_chunkr:
        parser = ChunkrParser(cache_dir)
    elif ext == ".pdf":
        parser = PDFParser(cache_dir)
    else:
        raise ValueError("Unsupported file type without CHUNKR_API_KEY. Only PDF is supported without Chunkr.")

    # Parse to markdown
    logger.info(f"[document_qa] parsing: {local_path} via {'chunkr' if use_chunkr else 'pymupdf' if ext=='.pdf' else 'unknown'}")
    document_markdown = await parser.parse(local_path)
    if not isinstance(document_markdown, str):
        document_markdown = str(document_markdown)
    if len(document_markdown) > text_limit:
        document_markdown = document_markdown[:text_limit] + "\n..."

    # Prepare LLM
    try:
        import openai
    except Exception as e:
        raise RuntimeError("openai package is required for document_qa") from e

    client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)

    system_prompt = "You are a helpful assistant for document analysis. " "Use ONLY the provided document content to answer. If unsure, say you don't know."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Document content (markdown):\n\n{document_markdown}"},
    ]
    messages.append({"role": "user", "content": f"Answer based on the document: {question}"})

    resp = await client.chat.completions.create(model=model, messages=messages)
    content = (resp.choices[0].message.content or "").strip()
    return content
