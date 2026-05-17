from __future__ import annotations
import json
import urllib.request
import urllib.parse
from typing import Any
from datapipe.sources.base import Source

_LIST_KEYS = ("data", "results", "items", "records", "rows", "content")


class HTTPSource(Source):
    def __init__(self, url: str, method: str = "GET", headers: dict[str, str] | None = None, params: dict[str, str] | None = None, timeout: int = 30) -> None:
        self.url = url
        self.method = method.upper()
        self.headers = headers or {}
        self.params = params or {}
        self.timeout = timeout
        self._row_count: int = 0

    def read(self) -> list[dict]:
        url = self.url
        if self.params:
            url = f"{url}?{urllib.parse.urlencode(self.params)}"
        req = urllib.request.Request(url, method=self.method)
        req.add_header("Accept", "application/json")
        for key, value in self.headers.items():
            req.add_header(key, value)
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            payload: Any = json.loads(resp.read().decode("utf-8"))
        if isinstance(payload, list):
            rows = payload
        elif isinstance(payload, dict):
            for key in _LIST_KEYS:
                if isinstance(payload.get(key), list):
                    rows = payload[key]
                    break
            else:
                rows = [payload]
        else:
            raise ValueError(f"HTTPSource: unexpected JSON type {type(payload).__name__!r} from {self.url!r}.")
        self._row_count = len(rows)
        return rows

    def __repr__(self) -> str:
        return f"HTTPSource(url={self.url!r}, method={self.method!r})"
