from abc import abstractmethod
from typing import Any
import httpx

from agentlin.tools.stateful_document.page_contents import PageContents


class Backend:
    @abstractmethod
    async def search(self, query: str, topn: int) -> PageContents:
        pass

    @abstractmethod
    async def fetch(self, url: str) -> PageContents:
        pass


class MinerUBackend(Backend):
    async def search(self, query: str, topn: int):
        pass
    async def fetch(self, url: str) -> PageContents:
        pass
