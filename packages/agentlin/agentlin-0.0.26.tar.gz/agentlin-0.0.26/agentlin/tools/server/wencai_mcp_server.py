import json
from typing_extensions import Annotated

from fastmcp import FastMCP
from loguru import logger
import requests


mcp = FastMCP(
    "iWencai Tool Server",
    version="0.1.0",
)


def request_chain(json: dict, timeout=60):
    langchain_server_url = "http://190.92.231.77:880/iwencai/dialog/chain/execute"
    langchain_headers = {
        "Host": "aime-langchain-engine-server",
        "X-Arsenal-Auth": "aime-reinforcement-learning-environment-access",
        "Content-Type": "application/json",
    }

    response = requests.post(langchain_server_url, headers=langchain_headers, json=json, timeout=timeout)
    return response


def run_Search(query):
    obj = {"chain_name": "Search", "req_type": "nostream", "human_message": query}

    req = request_chain(obj)
    resp = req.json()
    logger.debug("Search request:")
    logger.debug(json.dumps(obj, ensure_ascii=False, indent=2))
    logger.debug("Search response:")
    logger.debug(json.dumps(resp, ensure_ascii=False, indent=2))
    response = resp.get("response", {})
    if not response:
        return None

    results = response.get("result", [])
    if not results:
        return None

    result_data = results[0]
    raw_data: list[dict[str, str]] = result_data.get("raw_data", [])

    return raw_data


def run_Forecast(query):
    obj = {
        "chain_name": "Forecast",
        "req_type": "nostream",
        "user_id": "516341571",
        "session_id": "76aca1e22af21a8550af5998b3345997",
        "question_id": "74f72139-3a43-449b-abad-a27125c8fcfe",
        "trace_id": "20003020175249303327900000000540",
        "human_message": query,
    }

    req = request_chain(obj)
    resp = req.json()
    logger.debug("Forecast request:")
    logger.debug(json.dumps(obj, ensure_ascii=False, indent=2))
    logger.debug("Forecast response:")
    logger.debug(json.dumps(resp, ensure_ascii=False, indent=2))

    response = resp.get("response", {})
    if not response:
        return None

    results = response.get("result", [])
    if not results:
        return None

    return results


def search_content_to_message_content(search_result: dict):
    """
    "summary": "7月31日，同花顺跌3.13%，成交额32.96亿元。两融数据显示，当日同花顺获融资买入额4.54亿元，融资偿还4.99亿元，融资净买入-4504.68万元。截至7月31日，同花顺融资融券余额合计41.59亿元。 融资方面，同花顺当日融资买入4.54亿元。当前融资余额41.49亿元，占流通市值的2.92%，融资余额超过近一年50%分位水平，处于较高位。 融券方面，同花顺7月31日融券偿还300.00股，融券卖出2100.00股，按当日收盘价计算，卖出金额59.56万元；融券余量3.59万股，融券余额1018.12万元，超过近一年80%分位水平，处于高位。 2025年1月-3月，同花顺实现营业收入7.48亿元，同比增长20.90%；归母净利润1.20亿元，同比增长15.91%。分红方面，同花顺A股上市后累计派现79.38亿元。近三年，累计派现41.40亿元。 ",
    "image_url": null,
    "full_summary": "",
    "channel": "news",
    "title": "同花顺7月31日获融资买入4.54亿元，融资余额41.49亿元 同花顺_新浪财经_新浪网",
    "url": "http://finance.sina.com.cn/stock/aiassist/rzrq/2025-08-01/doc-infimssy6657511.shtml",
    "simhash": "b1685ef99540b944",
    "search_extra_info": {
        "search_burial_info": {
        "uid": "9ea9e623f292371d",
        "ab": {
            "scene_id": "xkqxpvhms",
            "layer_exp": [
            {
                "layer_id": "holistic_layer",
                "exp_id": "base"
            }
            ]
        },
        "id": "9ea9e623f292371d"
        }
    },
    "publish_source": "新浪",
    "publish_time": "2025-08-01",
    "msg_type": "news",
    "msg_id": "9ea9e623f292371d",
    "host_name": "finance.sina.com.cn",
    "image_type": null
    """
    texts = []
    # if "id" in search_result:
    #     texts.append(f"ID: {search_result['id']}")
    if "title" in search_result:
        texts.append(f"Title: {search_result['title']}")
    if "msg_id" in search_result:
        texts.append(f"msg_id: {search_result['msg_id']}")
    if "url" in search_result:
        texts.append(f"URL: {search_result['url']}")
    if "publish_time" in search_result:
        texts.append(f"Publish Time: {search_result['publish_time']}")
    if "summary" in search_result:
        texts.append(f"Summary: {search_result['summary']}")
    return "\n".join(texts)


def fulltext_content_to_message_content(fulltext_result: dict):
    texts = []
    if "title" in fulltext_result:
        texts.append(f"Title: {fulltext_result['title']}")
    if "msg_id" in fulltext_result:
        texts.append(f"msg_id: {fulltext_result['msg_id']}")
    if "url" in fulltext_result:
        texts.append(f"URL: {fulltext_result['url']}")
    if "publish_time" in fulltext_result:
        texts.append(f"Publish Time: {fulltext_result['publish_time']}")
    if "full_summary" in fulltext_result:
        texts.append(f"Full Summary: {fulltext_result['full_summary']}")
    if "content" in fulltext_result:
        texts.append(f"Content: {fulltext_result['content']}")
    return "\n".join(texts)


def forecast_content_to_message_content(forecast_result: dict):
    texts = []
    query_data = forecast_result.get("query_data", {})
    if "title" in query_data:
        texts.append(f"Title: {query_data['title']}")
    if "url" in query_data:
        texts.append(f"URL: {query_data['url']}")
    if "text" in forecast_result:
        texts.append(f"Forecast Result: {forecast_result['text']}")
    return "\n".join(texts)


@mcp.tool(
    name="Search",
    description="通用搜索引擎，用于获取新闻资讯和市场分析等非结构化信息",
)
def Search(
    query: Annotated[str, "自然语言查询"],
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


@mcp.tool(
    name="AccessingFullText",
    description="根据Search工具返回的msg_id或url，获取完整文本内容，用于深度阅读",
)
def AccessingFullText(
    id_string: Annotated[str, "msg_id or url"],
):
    if "," in id_string:
        id_list = id_string.split(",")
    else:
        id_list = [id_string]

    obj = {
        "chain_name": "WorkFlowCommon",
        "req_type": "nostream",
        "user_id": "516341571",
        "session_id": "76aca1e22af21a8550af5998b3345997",
        "question_id": "74f72139-3a43-449b-abad-a27125c8fcfe",
        "trace_id": "20003020175249303327900000000540",
        "add_info": {"work_flow": {"request_params": {"mode": "WORK_FLOW", "pipe_name": "17090", "input_variable_value": {"list": id_list}}}},
    }

    req = request_chain(obj)
    resp = req.json()
    logger.debug("AccessingFullText request:")
    logger.debug(json.dumps(obj, ensure_ascii=False, indent=2))
    logger.debug("AccessingFullText response:")
    logger.debug(json.dumps(resp, ensure_ascii=False, indent=2))

    response = resp.get("response", {})
    if not response:
        return None

    response_datas = response.get("datas", [])
    if not response_datas:
        return None

    response_data = response_datas[0]
    text: str = response_data.get("text", "")
    raw_data: list[dict[str, str]] = response_data.get("raw_data", [])

    block_list = []
    message_content = []

    # 如果有 raw_data，使用结构化数据
    if raw_data:
        for i, x in enumerate(raw_data):
            fulltext_result = {
                "type": "fulltext_result",
                "data": x,
                "id": i,
            }
            block_list.append(fulltext_result)

            text_content = {
                "type": "text",
                "text": fulltext_content_to_message_content(x),
                "id": i,
            }
            message_content.append(text_content)
    else:
        # 如果没有 raw_data，使用返回的 text
        summary_result = {
            "type": "fulltext_summary",
            "data": {"query_ids": id_string, "summary_text": text},
            "id": 0,
        }
        block_list.append(summary_result)

        text_content = {
            "type": "text",
            "text": f"Query: AccessingFullText for msg_id(s): {id_string}\nResult:\n{text}",
            "id": 0,
        }
        message_content.append(text_content)

    return {
        "message_content": message_content,
        "block_list": block_list,
    }


@mcp.tool(
    name="Forecast",
    description="预测工具，对资产价格进行预测分析，只支持A股股票短期预测",
)
def Forecast(
    query: Annotated[str, "A股标的"],
):
    results = run_Forecast(query)
    if not results:
        return {
            "message_content": [],
            "block_list": [],
        }

    block_list = []
    message_content = []

    for i, result_data in enumerate(results):
        query_data = result_data.get("query_data", {})
        title = query_data.get("title", "")
        if not title:
            continue

        forecast_result = {
            "type": "forecast_result",
            "data": result_data,
            "id": i,
        }
        block_list.append(forecast_result)

        text_content = {
            "type": "text",
            "text": forecast_content_to_message_content(result_data),
            "id": i,
        }
        message_content.append(text_content)

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
