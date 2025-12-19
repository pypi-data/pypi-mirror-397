from typing_extensions import Annotated
import json
import requests

from fastmcp import FastMCP
from loguru import logger


mcp = FastMCP(
    "AIME Tool Server",
    version="0.1.0",
)

tool_server_url = "https://internal-idc-equ.ainvest.com/ind/aime-langchain-engine-server/iwencai/dialog/chain/execute"
# tool_server_url = "http://127.0.0.1:8989/aime"


def run_Search(query):
    req = requests.post(
        tool_server_url,
        json={
            "chain_name": "Search",
            "req_type": "nostream",
            "human_message": query,
            "debug": "false",
            "source": "ths_mobile_yuyinzhushou",
        },
    )
    resp = req.json()
    raw_data = []
    try:
        resp_result = resp["response"]["result"][0]
        raw_data: list[dict[str, str]] = resp_result["raw_data"]
    except Exception as e:
        logger.error(f"请求失败: {e}")
        logger.error(f"响应内容: {json.dumps(resp, indent=2, ensure_ascii=False)}")
    return raw_data


def search_content_to_message_content(search_result: dict):
    texts = []
    # if "id" in search_result:
    #     texts.append(f"ID: {search_result['id']}")
    if "title" in search_result:
        texts.append(f"Title: {search_result['title']}")
    if "url" in search_result:
        texts.append(f"URL: {search_result['url']}")
    if "publish_time" in search_result:
        texts.append(f"Publish Time: {search_result['publish_time']}")
    if "summary" in search_result:
        texts.append(f"Summary: {search_result['summary']}")
    return "\n".join(texts)


@mcp.tool(
    name="Search",
    description="This is a general search engine.",
)
def Search(
    query: Annotated[str, "natural language query"],
):
    raw_data: list[dict[str, str]] = run_Search(query)
    block_list = []
    message_content = []
    for i, x in enumerate(raw_data):
        search_result = {
            "type": "search_result",
            "data": x,
            "id": i,
        }
        block_list.append(search_result)

        text = {
            "type": "text",
            "text": search_content_to_message_content(x),
            "id": i,
        }
        message_content.append(text)
    return {
        "message_content": message_content,
        "block_list": block_list,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7778, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    mcp.run("http", host=args.host, port=args.port, log_level="debug" if args.debug else "info")
