from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from app.services.providers.cache import MemoryCache


@dataclass(slots=True)
class CrossrefWork:
    title: str
    doi: str | None
    year: int | None
    venue: str | None
    authors: list[str]
    raw: dict[str, Any]


class CrossrefClient:
    base_url = "https://api.crossref.org"

    def __init__(self, mailto: str | None = None, timeout: float = 10.0, cache: MemoryCache | None = None) -> None:
        self.mailto = mailto
        self.timeout = timeout
        self.cache = cache or MemoryCache()

    def get_by_doi(self, doi: str) -> CrossrefWork | None:
        path = f"/works/{quote(doi)}"
        payload = self._get_json(path)
        message = payload.get("message")
        return self._normalize(message) if message else None

    def search(self, title: str, rows: int = 5) -> list[CrossrefWork]:
        query = urlencode({"query.title": title, "rows": rows})
        payload = self._get_json(f"/works?{query}")
        items = payload.get("message", {}).get("items", [])
        return [normalized for item in items if (normalized := self._normalize(item))]

    def _get_json(self, path: str) -> dict[str, Any]:
        cache_key = f"crossref:{path}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        url = f"{self.base_url}{path}"
        headers = {"User-Agent": self._user_agent()}
        with urlopen(Request(url, headers=headers), timeout=self.timeout) as response:
            return self.cache.set(cache_key, json.loads(response.read().decode("utf-8")))

    def _normalize(self, item: dict[str, Any] | None) -> CrossrefWork | None:
        if not item:
            return None
        title_list = item.get("title") or []
        authors = [
            " ".join(part for part in [author.get("given"), author.get("family")] if part)
            for author in item.get("author", [])
        ]
        year = None
        if item.get("published-print", {}).get("date-parts"):
            year = item["published-print"]["date-parts"][0][0]
        elif item.get("published-online", {}).get("date-parts"):
            year = item["published-online"]["date-parts"][0][0]
        return CrossrefWork(
            title=title_list[0] if title_list else "",
            doi=item.get("DOI"),
            year=year,
            venue=(item.get("container-title") or [None])[0],
            authors=[author for author in authors if author],
            raw=item,
        )

    def _user_agent(self) -> str:
        if self.mailto:
            return f"paper-reference-refactor/0.1 (mailto:{self.mailto})"
        return "paper-reference-refactor/0.1"
