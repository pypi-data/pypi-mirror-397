import requests
import json
import os
from typing import Optional


class DifyClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        proxies: Optional[dict[str, str]] = None,
        timeout=10,
    ):
        self.api_key = api_key or os.getenv("DIFY_API_KEY")
        if not self.api_key:
            raise ValueError("DIFY_API_KEY is not set")
        if proxies is None:
            http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
            https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
            proxy = {}
            if http_proxy:
                proxy["http"] = http_proxy
            if https_proxy:
                proxy["https"] = https_proxy
            if proxy:
                proxies = proxy
        self.proxies = proxies or {}
        self.timeout = timeout

    def call_api(self, user_id: str, query: str, **kwargs):
        url = "https://api.dify.ai/v1/workflows/run"
        payload = json.dumps(
            {
                "inputs": {
                    "q": query,
                },
                "response_mode": "blocking",
                "user": user_id,
                **kwargs,
            }
        )
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        response = requests.request(
            "POST",
            url,
            headers=headers,
            data=payload,
            proxies=self.proxies,
            timeout=self.timeout,
        )
        obj = response.json()
        if "data" in obj:
            obj = obj["data"]
        if "outputs" in obj:
            obj = obj["outputs"]
        return obj
