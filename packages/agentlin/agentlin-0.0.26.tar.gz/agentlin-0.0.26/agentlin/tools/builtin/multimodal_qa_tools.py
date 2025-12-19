import asyncio
import traceback
import os
from pathlib import Path
from typing import Optional

from loguru import logger

from agentlin.core.multimodal import _cache_dir
from agentlin.core.types import BaseTool, FunctionParameters, ToolParams, ToolResult
from agentlin.tools.core import tool_result_of_text
from agentlin.tools.tool_document import document_qa
from agentlin.tools.tool_audio import transcribe_audio
from agentlin.tools.tool_video import video_qa



class DocumentQATool(BaseTool):
    """Tool: Parse a document (local path or URL) and answer a question about it.

    Parameters:
        - document_path: string, required
        - question: string, required (ask a question about the document; can be a summary request)
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        cache_dir: Path | str | None = None,
        text_limit: int = 100_000,
        name: str = "document_qa",
        title: str = "Document Q&A",
        description: str = "Ask a question about a document (PDF or other supported formats via Chunkr) and get an answer using an LLM.",
    ) -> None:
        parameters: FunctionParameters = {
            "type": "object",
            "properties": {
                "document_path": {
                    "type": "string",
                    "description": "Local file path or HTTP(S) URL to the document (PDF or other formats if CHUNKR_API_KEY set).",
                },
                "question": {
                    "type": "string",
                    "description": "The question about the document (can also be something like 'Summarize the document').",
                },
            },
            "required": ["document_path", "question"],
            "additionalProperties": False,
        }
        super().__init__(
            name=name,
            title=title,
            description=description,
            parameters=parameters,
            strict=True,
        )
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._text_limit = text_limit
        self.cache_directory = os.getenv("CACHE_DIRECTORY", os.getcwd())
        self.cache_dir = _cache_dir("documents", cache_dir, self.cache_directory)

    async def execute(self, params: ToolParams) -> ToolResult:
        document_path = (params or {}).get("document_path")
        question = (params or {}).get("question")
        if not document_path or not isinstance(document_path, str):
            return tool_result_of_text("Invalid parameter: 'document_path' is required and must be a string.")
        if not question or not isinstance(question, str):
            return tool_result_of_text("Invalid parameter: 'question' is required and must be a string.")
        try:
            answer = await document_qa(
                document_path,
                question,
                api_key=self._api_key,
                base_url=self._base_url,
                model=self._model,
                cache_dir=self.cache_dir,
                text_limit=self._text_limit,
            )
            tr = tool_result_of_text(answer)
            tr.data = {
                "document_path": document_path,
                "model": self._model,
                "provider": "openai-compatible",
                "text_limit": self._text_limit,
            }
            return tr
        except Exception as e:
            logger.error(f"Document Q&A failed for {document_path}: {e}\n{traceback.format_exc()}")
            return tool_result_of_text(f"Document Q&A failed: {e}")


class AudioTranscriptionTool(BaseTool):
    """Tool: Transcribe an audio file from local path or URL.

    Parameters:
        - audio_path: string, required
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        cache_dir: Path | str | None = None,
        name: str = "transcribe_audio",
        title: str = "Transcribe Audio",
        description: str = "Transcribe an audio file (path or URL) using OpenAI and return verbose JSON.",
    ) -> None:
        parameters: FunctionParameters = {
            "type": "object",
            "properties": {
                "audio_path": {
                    "type": "string",
                    "description": "Local file path or HTTP(S) URL to the audio file.",
                }
            },
            "required": ["audio_path"],
            "additionalProperties": False,
        }
        super().__init__(
            name=name,
            title=title,
            description=description,
            parameters=parameters,
            strict=True,
        )
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.cache_directory = os.getenv("CACHE_DIRECTORY", os.getcwd())
        self.cache_dir = _cache_dir("audio", cache_dir, self.cache_directory)

    async def execute(self, params: ToolParams) -> ToolResult:
        audio_path = (params or {}).get("audio_path")
        if not audio_path or not isinstance(audio_path, str):
            return tool_result_of_text("Invalid parameter: 'audio_path' is required and must be a string.")
        try:
            result = await transcribe_audio(
                audio_path,
                api_key=self.api_key,
                base_url=self.base_url,
                model=self.model,
                cache_dir=self.cache_dir,
            )
            # Provide a concise text summary, with full JSON in data
            text = (
                f"Transcription completed.\n"
                f"Duration: {result.get('duration', 'n/a')}s\n"
                f"Text: {result.get('text', '')[:2000]}"  # truncate for message
            )
            tr = ToolResult(
                message_content=[{"type": "text", "text": text}],
                block_list=[{"type": "text", "text": text}],
                data=result,
            )
            return tr
        except Exception as e:
            logger.error(f"Audio transcription failed for {audio_path}: {e}\n{traceback.format_exc()}")
            return tool_result_of_text(f"Audio transcription failed: {e}")



class VideoQATool(BaseTool):
    """Tool: Ask a question about a video (local path or URL) using Google Gemini.

    Parameters:
            - video_url: string, required
            - question: string, required
    """

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        api_version: str = "v1alpha",
        mime_type: Optional[str] = None,
        name: str = "video_qa",
        title: str = "Video Q&A",
        description: str = "Ask a question about a video using Google Gemini and return the answer.",
    ) -> None:
        parameters: FunctionParameters = {
            "type": "object",
            "properties": {
                "video_url": {
                    "type": "string",
                    "description": "Local file path or HTTP(S) URL to the video.",
                },
                "question": {
                    "type": "string",
                    "description": "The question to ask about the video content.",
                },
            },
            "required": ["video_url", "question"],
            "additionalProperties": False,
        }
        super().__init__(
            name=name,
            title=title,
            description=description,
            parameters=parameters,
            strict=True,
        )
        self._api_key = api_key
        self._model = model
        self._api_version = api_version
        self._mime_type = mime_type

    async def execute(self, params: ToolParams) -> ToolResult:
        video_url = (params or {}).get("video_url")
        question = (params or {}).get("question")
        if not video_url or not isinstance(video_url, str):
            return tool_result_of_text("Invalid parameter: 'video_url' is required and must be a string.")
        if not question or not isinstance(question, str):
            return tool_result_of_text("Invalid parameter: 'question' is required and must be a string.")
        try:
            text = await video_qa(
                video_url,
                question,
                api_key=self._api_key,
                model=self._model,
                api_version=self._api_version,
                mime_type=self._mime_type,
            )
            tr = tool_result_of_text(text)
            # Include helpful context in data
            tr.data = {
                "video_url": video_url,
                "model": self._model,
                "provider": "google-genai",
                "api_version": self._api_version,
            }
            return tr
        except Exception as e:
            logger.error(f"Video Q&A failed: {e}\n{traceback.format_exc()}")
            return tool_result_of_text(f"Video Q&A failed: {e}")
