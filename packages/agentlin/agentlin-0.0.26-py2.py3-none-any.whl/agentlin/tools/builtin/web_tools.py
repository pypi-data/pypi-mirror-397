
from agentlin.core.types import BaseTool, ToolParams, ToolResult, FunctionParameters
from agentlin.code_interpreter.display_search_result import search_result_to_text
from agentlin.tools.core import tool_result_of_text
from agentlin.tools.tool_web_fetch import web_fetch
from agentlin.tools.tool_search import (
    BaiduSearch,
    DuckDuckGoSearch,
    GoogleSearch,
    JinaSearch,
)


class WebFetchTool(BaseTool):
    """BaseTool 子类：抓取多个 URL 的网页主内容与标题。

    参数：
      - urls: string[] 必填，要抓取的 URL 列表
      - max_concurrent: int 可选，并发抓取上限（默认 3，范围 1-10）
      - trim_length: int 可选，单篇内容最大截断长度（默认 10000）
    """

    def __init__(
        self,
        *,
        name: str = "web_fetch",
        title: str = "Web Fetch",
        description: str = "Fetch specific URLs to extract title and main content.",
        default_max_concurrent: int = 3,
        default_trim_length: int = 10000,
    ) -> None:
        parameters: FunctionParameters = {
            "type": "object",
            "properties": {
                "urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of URLs to fetch",
                },
                "max_concurrent": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "default": default_max_concurrent,
                    "description": "Maximum concurrent requests (1-10)",
                },
                "trim_length": {
                    "type": "integer",
                    "minimum": 200,
                    "maximum": 200000,
                    "default": default_trim_length,
                    "description": "Max characters to keep per content",
                },
            },
            "required": ["urls"],
            "additionalProperties": False,
        }
        super().__init__(
            name=name,
            title=title,
            description=description,
            parameters=parameters,
            strict=True,
        )
        self.default_max_concurrent = default_max_concurrent
        self.default_trim_length = default_trim_length

    async def execute(self, params: ToolParams) -> ToolResult:
        urls = (params or {}).get("urls")
        max_concurrent = (params or {}).get("max_concurrent", self.default_max_concurrent)
        trim_length = (params or {}).get("trim_length", self.default_trim_length)

        # 参数校验
        if not isinstance(urls, list) or not all(isinstance(u, str) and u.strip() for u in urls):
            return tool_result_of_text("Invalid parameter: 'urls' must be a non-empty array of strings.")
        try:
            max_concurrent = int(max_concurrent)
        except Exception:
            max_concurrent = self.default_max_concurrent
        if max_concurrent < 1:
            max_concurrent = 1
        if max_concurrent > 10:
            max_concurrent = 10
        try:
            trim_length = int(trim_length)
        except Exception:
            trim_length = self.default_trim_length
        trim_length = max(200, min(200000, trim_length))

        tool_response = await web_fetch(urls, max_concurrent=max_concurrent, trim_length=trim_length)
        return ToolResult(
            message_content=tool_response.get("message_content", []),
            block_list=tool_response.get("block_list", []),
            data=tool_response.get("data", {}),
        )


class WebSearchTool(BaseTool):
    """BaseTool 子类：统一的网页搜索工具。

    参数：
            - query: string 必填，搜索关键词
            - num_results: int 可选，返回结果数量（默认 5，范围 1-20）

        初始化参数（构造时注入，运行时不可更改）：
            - engine: 'google' | 'duckduckgo' | 'baidu' | 'jina'（默认 'duckduckgo'）
            - search_banned_sites: string[] 排除的站点前缀列表（如 'huggingface.co'）
            - search_params: dict 透传给具体引擎的参数
    """

    ALLOWED_ENGINES = ["google", "duckduckgo", "baidu", "jina"]

    def __init__(
        self,
        *,
        name: str = "web_search",
        title: str = "Web Search",
        description: str = "Search the web via a configured engine and return summarized results.",
        engine: str = "duckduckgo",
        search_banned_sites: list[str] | None = None,
        search_params: dict | None = None,
        default_num_results: int = 5,
    ) -> None:
        if engine not in self.ALLOWED_ENGINES:
            engine = "duckduckgo"
        if not isinstance(default_num_results, int) or default_num_results < 1:
            default_num_results = 5
        if default_num_results > 20:
            default_num_results = 20
        search_banned_sites = search_banned_sites or []
        search_params = search_params or {}

        parameters: FunctionParameters = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query string to search for",
                },
                "num_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20,
                    "default": default_num_results,
                    "description": "Number of results to return (1-20)",
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        }
        super().__init__(
            name=name,
            title=title,
            description=description,
            parameters=parameters,
            strict=True,
        )
        self.engine_name = engine
        self.default_num_results = default_num_results

        # 初始化具体的搜索器实例
        if engine == "google":
            self.searcher = GoogleSearch(search_banned_sites, search_params)
        elif engine == "duckduckgo":
            self.searcher = DuckDuckGoSearch(search_banned_sites)
        elif engine == "baidu":
            self.searcher = BaiduSearch(search_banned_sites)
        elif engine == "jina":
            self.searcher = JinaSearch(search_banned_sites, search_params)
        else:
            # 理论上不会到这里，做一次兜底
            self.searcher = DuckDuckGoSearch(search_banned_sites)

    async def execute(self, params: ToolParams) -> ToolResult:
        params = params or {}
        query = params.get("query")
        num_results = params.get("num_results", self.default_num_results)

        # 参数校验
        if not isinstance(query, str) or not query.strip():
            return tool_result_of_text("Invalid parameter: 'query' must be a non-empty string.")
        try:
            num_results = int(num_results)
        except Exception:
            num_results = self.default_num_results
        if num_results < 1:
            num_results = 1
        if num_results > 20:
            num_results = 20

        try:
            results = await self.searcher.search(query.strip(), num_results)
        except Exception as e:
            return tool_result_of_text(f"Web search failed: {e}")

        message_content = []
        block_list = []
        message_content.append({"type": "text", "text": f"Query: {query}\nResults Found from {self.engine_name}:\n"})
        for align_id, result in enumerate(results):
            text = search_result_to_text(result)
            message_content.append({"type": "text", "text": text, "id": align_id})
            block_list.append({"type": "search_result", "data": result, "id": align_id})

        return ToolResult(
            message_content=message_content,
            block_list=block_list,
            data={
                "engine": self.engine_name,
                "query": query.strip(),
                "results": results,
            },
        )


def load_tools() -> list[BaseTool]:
    return [
        WebFetchTool(),
        WebSearchTool(engine="google", name="google_search"),
        WebSearchTool(engine="duckduckgo", name="duckduckgo_search"),
        WebSearchTool(engine="baidu", name="baidu_search"),
        WebSearchTool(engine="jina", name="jina_search"),
    ]
