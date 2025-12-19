import os
import sys

from loguru import logger
from fastapi import Request
from pydantic import BaseModel
from sglang.srt.entrypoints.openai.protocol import ChatCompletionMessageParam
from sglang.srt.entrypoints.http_server import app

"""
SGLang Server with Additional Tokenizer Endpoints

This module patches the SGLang server to add additional tokenizer endpoints:
- /tokenize: Tokenize text to token IDs
- /detokenize: Convert token IDs back to text
- /tokenize_with_template: Apply chat template and tokenize messages

Usage:
    ```sh
    python launch_server.py {other args}
    # i.e.
    # python -m sglang.launch_server {other args}
    ```

Example:
    python sgl_server.py --port 30000
"""

class TokenizeRequest(BaseModel):
    text: str


class TokenizeMessageRequest(BaseModel):
    messages: list[ChatCompletionMessageParam]


class TokenizeResponse(BaseModel):
    text: str
    token_ids: list[int]


class DeTokenizeRequest(BaseModel):
    token_ids: list[int]


class DeTokenizeResponse(BaseModel):
    text: str
    token_ids: list[int]



@app.post("/tokenize")
async def tokenize(raw_request: Request) -> TokenizeResponse:
    from sglang.srt.entrypoints.http_server import _global_state

    request_json = await raw_request.json()
    request = TokenizeRequest(**request_json)
    token_ids = _global_state.tokenizer_manager.tokenizer.encode(request.text)

    return TokenizeResponse(token_ids=token_ids, text=request.text)

@app.post("/detokenize")
async def detokenize(raw_request: Request) -> DeTokenizeResponse:
    from sglang.srt.entrypoints.http_server import _global_state

    request_json = await raw_request.json()
    request = DeTokenizeRequest(**request_json)
    text = _global_state.tokenizer_manager.tokenizer.decode(request.token_ids)

    return DeTokenizeResponse(token_ids=request.token_ids, text=text)

@app.post("/tokenize_with_template")
async def tokenize_with_template(raw_request: Request) -> TokenizeResponse:
    from sglang.srt.entrypoints.http_server import _global_state

    request_json = await raw_request.json()
    request = TokenizeMessageRequest(**request_json)

    token_ids = _global_state.tokenizer_manager.tokenizer.apply_chat_template(
        request.messages, tokenize=True, add_generation_prompt=False
    )
    text = _global_state.tokenizer_manager.tokenizer.decode(token_ids)

    return TokenizeResponse(token_ids=token_ids, text=text)

logger.info("Monkey patching tokenizer endpoints")


if __name__ == "__main__":
    from sglang.srt.utils import kill_process_tree
    from sglang.srt.server_args import prepare_server_args
    from sglang.srt.entrypoints.http_server import launch_server
    server_args = prepare_server_args(sys.argv[1:])

    try:
        launch_server(server_args)
    finally:
        kill_process_tree(os.getpid(), include_parent=False)
