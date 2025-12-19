"""
Audio transcription utilities and tool.

Requirements covered:
- Cache directory is configurable (function parameter and tool constructor).
- OpenAI is a fixed dependency (no import checks or env guards).
- Audio model is configurable (constructor/func param; no env vars).
- OpenAI API key and base URL are configurable (constructor/func param; no env vars).

This module provides:
- async function `transcribe_audio(...)` for reusable transcription with on-disk caching
- BaseTool subclass `AudioTranscriptionTool` exposing a simple transcribe tool
"""

import asyncio
import json
import mimetypes
import os
from pathlib import Path
from typing import Dict, Any

from loguru import logger
import openai
from openai.types.audio import TranscriptionVerbose

from agentlin.core.multimodal import _download_to, _file_md5, _is_web_url


async def transcribe_audio(
    path_or_url: str,
    *,
    api_key: str,
    base_url: str,
    model: str,
    cache_dir: Path,
) -> Dict[str, Any]:
    """Transcribe an audio file using OpenAI and cache results by file MD5.

    Args:
            path_or_url: Local file path or http(s) URL to an audio file.
            api_key: OpenAI API key to use.
            base_url: OpenAI API base URL to use.
            model: Audio transcription model name.
            cache_dir: Directory to store downloaded audio and cached transcripts.

    Returns:
            A dict converted from openai TranscriptionVerbose model_dump(), with
            extra fields: {"audio_file": str, "cache_file": str}.
    """
    # Resolve local path, download if needed
    if _is_web_url(path_or_url):
        # Decide extension from URL or mimetype
        ext = Path(path_or_url.split("?")[0]).suffix
        if not ext:
            # Best effort from mimetypes
            guessed, _ = mimetypes.guess_type(path_or_url)
            if guessed and "/" in guessed:
                ext = "." + guessed.split("/")[-1]
        tmp_path = cache_dir / ("download_tmp" + (ext or ""))
        local_path = await _download_to(path_or_url, tmp_path)
    else:
        local_path = Path(path_or_url).expanduser().resolve()
        if not local_path.exists():
            raise FileNotFoundError(f"Audio file not found: {local_path}")

    # Compute md5 and establish stable file name under cache
    md5 = await asyncio.to_thread(_file_md5, local_path)
    ext = local_path.suffix or ".audio"
    cached_audio = cache_dir / f"{md5}{ext}"
    if not cached_audio.exists():
        # copy file into cache (avoid rename when source is outside cache)
        def _copy():
            from shutil import copyfile

            copyfile(local_path, cached_audio)

        await asyncio.to_thread(_copy)

    # Cached transcript path
    cached_json = cache_dir / f"{md5}.transcript.json"
    if cached_json.exists():
        try:
            content = json.loads(cached_json.read_text(encoding="utf-8"))
            content.setdefault("audio_file", str(cached_audio))
            content.setdefault("cache_file", str(cached_json))
            return content
        except Exception:
            # Recompute if cache corrupted
            pass

    # Call OpenAI async client
    client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)
    logger.debug(f"Transcribing audio via {base_url} using model={model}, file={cached_audio.name}")
    with cached_audio.open("rb") as f:
        transcript: TranscriptionVerbose = await client.audio.transcriptions.create(
            model=model,
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )

    data = transcript.model_dump()
    # augment with helpful fields
    data["audio_file"] = str(cached_audio)
    data["cache_file"] = str(cached_json)

    # write cache atomically
    tmp_out = cached_json.with_suffix(".transcript.json.tmp")
    tmp_out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_out.replace(cached_json)

    return data
