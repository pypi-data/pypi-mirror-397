import functools
import asyncio
import logging
import os
from abc import abstractmethod
from typing import Callable, ParamSpec, TypeVar
from typing_extensions import Annotated
from urllib.parse import quote

from aiohttp import ClientSession, ClientTimeout
from tenacity import (
    after_log,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from agentlin.tools.stateful_browser.page_contents import (
    Extract,
    FetchResult,
    PageContents,
    get_domain,
    process_html,
)

from loguru import logger

VIEW_SOURCE_PREFIX = "view-source:"


class BackendError(Exception):
    pass


P = ParamSpec("P")
R = TypeVar("R")


def with_retries(
    func: Callable[P, R],
    num_retries: int,
    max_wait_time: float,
) -> Callable[P, R]:
    if num_retries > 0:
        retry_decorator = retry(
            stop=stop_after_attempt(num_retries),
            wait=wait_exponential(
                multiplier=1,
                min=2,
                max=max_wait_time,
            ),
            before_sleep=before_sleep_log(logger, logging.INFO),
            after=after_log(logger, logging.INFO),
            retry=retry_if_exception_type(Exception),
        )
        return retry_decorator(func)
    else:
        return func


def maybe_truncate(text: str, num_chars: int = 1024) -> str:
    if len(text) > num_chars:
        text = text[: (num_chars - 3)] + "..."
    return text


class Backend:
    def __init__(self, source: Annotated[str, "Description of the backend source"]):
        self.source = source

    @abstractmethod
    async def search(
        self,
        query: str,
        topn: int,
    ) -> PageContents:
        pass

    @abstractmethod
    async def fetch(
        self,
        url: str,
    ) -> PageContents:
        pass

    async def _post(self, endpoint: str, payload: dict) -> dict:
        headers = {"x-api-key": self._get_api_key()}
        async with ClientSession() as session:
            async with session.post(f"{self.BASE_URL}{endpoint}", json=payload, headers=headers) as resp:
                if resp.status != 200:
                    raise BackendError(f"{self.__class__.__name__} error {resp.status}: {await resp.text()}")
                return await resp.json()

    async def _get(self, endpoint: str, params: dict) -> dict:
        headers = {"x-api-key": self._get_api_key()}
        async with ClientSession() as session:
            async with session.get(f"{self.BASE_URL}{endpoint}", params=params, headers=headers) as resp:
                if resp.status != 200:
                    raise BackendError(f"{self.__class__.__name__} error {resp.status}: {await resp.text()}")
                return await resp.json()


class ExaBackend(Backend):
    """Backend that uses the Exa Search API."""

    BASE_URL: str = "https://api.exa.ai"

    def __init__(
        self,
        *,
        source: Annotated[str, "Description of the backend source"],
        api_key: Annotated[str | None, "Exa API key. Uses EXA_API_KEY environment variable if not provided."] = None,
    ):
        super().__init__(source=source)
        self.api_key = api_key

    def _get_api_key(self) -> str:
        key = self.api_key or os.environ.get("EXA_API_KEY")
        if not key:
            raise BackendError("Exa API key not provided")
        return key

    async def search(self, query: str, topn: int) -> PageContents:
        data = await self._post(
            "/search",
            {"query": query, "numResults": topn, "contents": {"text": True, "summary": True}},
        )
        import json
        print(json.dumps(data, indent=2))
        # make a simple HTML page to work with browser format
        titles_and_urls = [(result["title"], result["url"], result["summary"]) for result in data["results"]]
        html_page = f"""
<html><body>
<h1>Search Results</h1>
<ul>
{"".join([f"<li><a href='{url}'>{title}</a> {summary}</li>" for title, url, summary in titles_and_urls])}
</ul>
</body></html>
"""

        return process_html(
            html=html_page,
            url=f"search://{quote(query)}?max_results={topn}",
            title=query,
            display_urls=True,
        )

    async def fetch(self, url: str) -> PageContents:
        is_view_source = url.startswith(VIEW_SOURCE_PREFIX)
        if is_view_source:
            url = url[len(VIEW_SOURCE_PREFIX) :]
        data = await self._post(
            "/contents",
            {"urls": [url], "text": {"includeHtmlTags": True}},
        )
        results = data.get("results", [])
        if not results:
            raise BackendError(f"No contents returned for {url}")
        return process_html(
            html=results[0].get("text", ""),
            url=url,
            title=results[0].get("title", ""),
            display_urls=True,
        )


class YouComBackend(Backend):
    """Backend that uses the You.com Search API."""

    BASE_URL: str = "https://api.ydc-index.io"

    def __init__(
        self,
        *,
        source: Annotated[str, "Description of the backend source"],
        api_key: Annotated[str | None, "You.com API key. Uses YDC_API_KEY environment variable if not provided."] = None,
    ):
        super().__init__(source=source)
        self.api_key = api_key

    def _get_api_key(self) -> str:
        key = os.environ.get("YDC_API_KEY")
        if not key:
            raise BackendError("You.com API key not provided")
        return key

    async def search(self, query: str, topn: int) -> PageContents:
        data = await self._get(
            "/v1/search",
            {"query": query, "count": topn},
        )
        # make a simple HTML page to work with browser format
        web_titles_and_urls, news_titles_and_urls = [], []
        if "web" in data["results"]:
            web_titles_and_urls = [(result["title"], result["url"], result["snippets"]) for result in data["results"]["web"]]
        if "news" in data["results"]:
            news_titles_and_urls = [(result["title"], result["url"], result["description"]) for result in data["results"]["news"]]
        titles_and_urls = web_titles_and_urls + news_titles_and_urls
        html_page = f"""
<html><body>
<h1>Search Results</h1>
<ul>
{"".join([f"<li><a href='{url}'>{title}</a> {summary}</li>" for title, url, summary in titles_and_urls])}
</ul>
</body></html>
"""

        return process_html(
            html=html_page,
            url=f"search://{quote(query)}?max_results={topn}",
            title=query,
            display_urls=True,
        )

    async def fetch(self, url: str) -> PageContents:
        is_view_source = url.startswith(VIEW_SOURCE_PREFIX)
        if is_view_source:
            url = url[len(VIEW_SOURCE_PREFIX) :]
        data = await self._post(
            "/v1/contents",
            {"urls": [url], "livecrawl_formats": "html"},
        )
        if not data:
            raise BackendError(f"No contents returned for {url}")
        if "html" not in data[0]:
            raise BackendError(f"No HTML returned for {url}")
        return process_html(
            html=data[0].get("html", ""),
            url=url,
            title=data[0].get("title", ""),
            display_urls=True,
        )
