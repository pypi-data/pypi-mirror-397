"""
Video Q&A via Google Gemini (genai)

Requirements addressed:
- Parameters are configurable in the abstracted function and passed from the BaseTool subclass constructor
- genai / openai are fixed dependencies: no import checks, no env-var reads
- Video model is configurable (via constructor/function params)
- API key is configurable (via constructor/function params)

Refs:
- https://github.com/googleapis/python-genai
- https://ai.google.dev/gemini-api/docs/api-key
"""
from typing import Optional

from loguru import logger
from google import genai
from google.genai.types import HttpOptions, Part

from agentlin.core.multimodal import _is_web_url


def _to_video_part(video_url: str, mime_type: Optional[str] = None) -> Part:
    """Create a genai Part for a video input.

    If a http(s) URL, we pass mime_type if provided; otherwise let SDK infer or remote server resolve.
    For non-http path, we just pass file_uri directly.
    """
    if _is_web_url(video_url):
        return Part.from_uri(file_uri=video_url, mime_type=mime_type or "video/mp4")
    return Part.from_uri(file_uri=video_url)


async def video_qa(
    video_url: str,
    question: str,
    *,
    api_key: str,
    model: str,
    api_version: str = "v1alpha",
    mime_type: Optional[str] = None,
) -> str:
    """Ask a question about a video using Google's Gemini models.

    Args:
        video_url: Local path or HTTP(S) URL to the video content.
        question: The question to ask about the video.
        api_key: Google Generative AI API key.
        model: Gemini video-capable model, e.g., "gemini-1.5-flash"/"gemini-1.5-pro".
        api_version: genai API version (default v1alpha).
        mime_type: Optional mime type hint for remote URLs (default "video/mp4").

    Returns:
        Response text string produced by the model.
    """
    if not video_url or not isinstance(video_url, str):
        raise ValueError("'video_url' must be a non-empty string")
    if not question or not isinstance(question, str):
        raise ValueError("'question' must be a non-empty string")

    client = genai.Client(api_key=api_key, http_options=HttpOptions(api_version=api_version))
    video_part = _to_video_part(video_url, mime_type=mime_type)

    logger.debug(f"Calling Gemini model={model} for video QA. url={video_url}")
    resp = client.models.generate_content(
        model=model,
        contents=[question, video_part],
    )
    # The SDK exposes .text for the aggregated text output
    return getattr(resp, "text", str(resp))

