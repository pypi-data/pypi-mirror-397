import os
import re
from typing_extensions import Literal, Optional

import aiohttp
from bs4 import BeautifulSoup
from loguru import logger

from agentlin.code_interpreter.types import SearchResult


class ContentFilter:
    def __init__(self, banned_sites: list[str] = None):
        if banned_sites:
            self.RE_MATCHED_SITES = re.compile(r"^(" + "|".join(banned_sites) + r")")
        else:
            self.RE_MATCHED_SITES = None

    def filter_results(self, results: list[dict], limit: int, key: str = "link") -> list[dict]:
        # can also use search operator `-site:huggingface.co`
        # ret: {title, link, snippet, position, | sitelinks}
        res = []
        for result in results:
            if self.RE_MATCHED_SITES is None or not self.RE_MATCHED_SITES.match(result[key]):
                res.append(result)
            if len(res) >= limit:
                break
        return res


class BaiduSearch:
    """Baidu Search."""

    def __init__(self, search_banned_sites: list[str] = []) -> None:
        self.url = "https://www.baidu.com/s"
        self.headers = {
            "User-Agent": """Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/120.0.0.0 Safari/537.36""",
            "Referer": "https://www.baidu.com",
        }
        self.content_filter = ContentFilter(search_banned_sites) if search_banned_sites else None

    async def search(self, query: str, num_results: int = 5) -> list[SearchResult]:
        """standard search interface that returns a list of SearchResult."""
        raw_results = await self.search_baidu(query)
        # map to SearchResult
        mapped: list[SearchResult] = []
        for idx, r in enumerate(raw_results, 1):
            sr: SearchResult = {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "abstract": r.get("abstract"),
                "content": None,
                "error": None,
                "result_id": None,
                "publish_time": None,
                "id": idx,
            }
            mapped.append(sr)
        # filter by banned sites and limit
        if self.content_filter:
            mapped = self.content_filter.filter_results(mapped, num_results, key="url")  # type: ignore[arg-type]
        else:
            mapped = mapped[:num_results]
        return mapped

    async def search_baidu(self, query: str) -> list[dict[str, str]]:
        """Search Baidu using web scraping to retrieve relevant search results.

        - WARNING: Uses web scraping which may be subject to rate limiting or anti-bot measures.

        Returns:
            Example result:
            {
                'title': '百度百科',
                'abstract': '百度百科是一部内容开放、自由的网络百科全书...',
                'url': 'https://baike.baidu.com/'
            }
        """
        params = {"wd": query, "rn": "20"}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=self.headers, params=params) as response:
                response.raise_for_status()  # avoid cache error!
                results = await response.text(encoding="utf-8")

        soup = BeautifulSoup(results, "html.parser")
        results = []
        for idx, item in enumerate(soup.select(".result"), 1):
            title_element = item.select_one("h3 > a")
            title = title_element.get_text(strip=True) if title_element else ""
            link = title_element["href"] if title_element else ""
            desc_element = item.select_one(".c-abstract, .c-span-last")
            desc = desc_element.get_text(strip=True) if desc_element else ""

            results.append(
                {
                    "title": title,
                    "abstract": desc,
                    "url": link,
                }
            )
        if len(results) == 0:
            logger.warning(f"No results found from Baidu search: {query}")
        return results


class DuckDuckGoSearch:
    """DuckDuckGo Search.

    - repo: https://github.com/deedy5/ddgs
    """

    def __init__(self, search_banned_sites: list[str] = []) -> None:
        try:
            from ddgs import DDGS
        except ImportError as e:
            raise ImportError("Please install ddgs first: `pip install ddgs`") from e
        self.ddgs = DDGS()
        self.content_filter = ContentFilter(search_banned_sites) if search_banned_sites else None

    async def search(self, query: str, num_results: int = 5) -> list[SearchResult]:
        """standard search interface that returns a list of SearchResult."""
        raw = await self.search_duckduckgo(query)
        # Ensure list
        raw_list = list(raw) if not isinstance(raw, list) else raw
        # map to SearchResult
        mapped: list[SearchResult] = []
        for idx, r in enumerate(raw_list, 1):
            sr: SearchResult = {
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "abstract": r.get("body"),
                "content": None,
                "error": None,
                "result_id": None,
                "publish_time": None,
                "id": idx,
            }
            mapped.append(sr)
        # filter by banned sites and limit
        if self.content_filter:
            mapped = self.content_filter.filter_results(mapped, num_results, key="url")  # type: ignore[arg-type]
        else:
            mapped = mapped[:num_results]
        return mapped

    async def search_duckduckgo(self, query: str) -> list:
        """Use DuckDuckGo search engine to search for information on the given query.

        Returns:
            [{
                "title": ...
                "href": ...
                "body": ...
            }]
        """
        results = self.ddgs.text(query, max_results=100)
        return results


class GoogleSearch:
    """Google Search.

    - API key: `SERPER_API_KEY`
    """

    def __init__(self, search_banned_sites: list[str] = [], search_params: dict = {}):
        self.serper_url = r"https://google.serper.dev/search"
        self.serper_header = {
            "X-API-KEY": os.getenv("SERPER_API_KEY"),
            "Content-Type": "application/json",
        }
        self.search_params = search_params
        self.search_banned_sites = search_banned_sites
        self.content_filter = ContentFilter(search_banned_sites) if search_banned_sites else None

    async def search(self, query: str, num_results: int = 5) -> list[SearchResult]:
        """standard search interface that returns a list of SearchResult."""
        res = await self.search_google(query)
        organic = res.get("organic", []) if isinstance(res, dict) else []
        # map to SearchResult
        mapped: list[SearchResult] = []
        for idx, r in enumerate(organic, 1):
            publish_time = r.get("date") or r.get("publishedTime") or r.get("published_date")
            sr: SearchResult = {
                "title": r.get("title", ""),
                "url": r.get("link", ""),
                "abstract": r.get("snippet"),
                "content": None,
                "error": None,
                "result_id": None,
                "publish_time": publish_time,
                "id": idx,
            }
            mapped.append(sr)
        # filter by banned sites and limit
        if self.content_filter:
            mapped = self.content_filter.filter_results(mapped, num_results, key="url")  # type: ignore[arg-type]
        else:
            mapped = mapped[:num_results]
        return mapped

    async def search_google(self, query: str) -> dict:
        """Call the serper.dev API and cache the results."""
        params = {"q": query, **self.search_params, "num": 10}  # fetch and cache the results
        async with aiohttp.ClientSession() as session:
            async with session.post(self.serper_url, headers=self.serper_header, json=params) as response:
                response.raise_for_status()  # avoid cache error!
                results = await response.json()
                return results


class JinaSearch:
    """Search service provided by Jina

    - API key: `JINA_API_KEY`
    """

    def __init__(self, search_banned_sites: list[str] = [], search_params: dict = {}):
        self.jina_url = "https://s.jina.ai/"
        self.jina_header = {
            "Accept": "application/json",
            "Authorization": f"Bearer {os.getenv('JINA_API_KEY')}",
            "X-Respond-With": "no-content",  # do not return content
        }
        self.search_params = search_params
        self.content_filter = ContentFilter(search_banned_sites) if search_banned_sites else None

    async def search(self, query: str, num_results: int = 5) -> list[SearchResult]:
        """standard search interface that returns a list of SearchResult."""
        res = await self.search_jina(query)
        data = res.get("data", []) if isinstance(res, dict) else []
        # map to SearchResult
        mapped: list[SearchResult] = []
        for idx, r in enumerate(data, 1):
            sr: SearchResult = {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "abstract": r.get("description"),
                "content": None,  # we requested no-content via header
                "error": None,
                "result_id": None,
                "publish_time": None,
                "id": idx,
            }
            mapped.append(sr)
        # filter by banned sites and limit
        if self.content_filter:
            mapped = self.content_filter.filter_results(mapped, num_results, key="url")  # type: ignore[arg-type]
        else:
            mapped = mapped[:num_results]
        return mapped

    async def search_jina(self, query: str) -> dict:
        """Call the Jina API and cache the results.

        Ref: https://jina.ai/api-dashboard

        Returns:
            {
                "data": [{
                    "title": ...
                    "url": ...
                    "description": ...
                    "content": ...
                    "metadata", "external", "usage": ...
                }]
            }
        """
        params = {"q": query, **self.search_params}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.jina_url, headers=self.jina_header, params=params) as response:
                response.raise_for_status()
                results = await response.json()
                return results


async def web_search(
    engine: Literal["google", "duckduckgo", "baidu", "jina"],
    query: str,
    num_results: int = 5,
    search_banned_sites: list[str] = [],
    search_params: dict = {},
) -> list[SearchResult]:
    """Unified web search interface.

    Args:
        engine: Search engine to use.
        query: Query string.
        num_results: Number of results to return.
        search_banned_sites: List of site domains to exclude from results.
        search_params: Additional search parameters specific to the engine.

    Returns:
        A list of SearchResult objects.
    """
    if engine == "google":
        searcher = GoogleSearch(search_banned_sites, search_params)
    elif engine == "duckduckgo":
        searcher = DuckDuckGoSearch(search_banned_sites)
    elif engine == "baidu":
        searcher = BaiduSearch(search_banned_sites)
    elif engine == "jina":
        searcher = JinaSearch(search_banned_sites, search_params)
    else:
        raise ValueError(f"Unsupported search engine: {engine}")

    return await searcher.search(query, num_results)
