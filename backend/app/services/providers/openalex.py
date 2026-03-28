from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.services.providers.cache import MemoryCache


@dataclass(slots=True)
class OpenAlexWork:
    work_id: str
    title: str
    doi: str | None
    year: int | None
    venue: str | None
    authors: list[dict[str, Any]]
    raw: dict[str, Any]


class OpenAlexClient:
    base_url = "https://api.openalex.org"

    def __init__(self, mailto: str | None = None, timeout: float = 10.0, cache: MemoryCache | None = None) -> None:
        self.mailto = mailto
        self.timeout = timeout
        self.cache = cache or MemoryCache()

    def get_by_doi(self, doi: str) -> OpenAlexWork | None:
        query = urlencode({"filter": f"doi:https://doi.org/{doi}"})
        payload = self._get_json(f"/works?{query}")
        results = payload.get("results", [])
        return self._normalize(results[0]) if results else None

    def search(self, title: str, per_page: int = 5) -> list[OpenAlexWork]:
        query = urlencode({"search": title, "per-page": per_page, "mailto": self.mailto or ""})
        payload = self._get_json(f"/works?{query}")
        return [normalized for item in payload.get("results", []) if (normalized := self._normalize(item))]

    def _get_json(self, path: str) -> dict[str, Any]:
        cache_key = f"openalex:{path}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        url = f"{self.base_url}{path}"
        with urlopen(Request(url, headers={"User-Agent": "paper-reference-refactor/0.1"}), timeout=self.timeout) as response:
            return self.cache.set(cache_key, json.loads(response.read().decode("utf-8")))

    def _normalize(self, item: dict[str, Any] | None) -> OpenAlexWork | None:
        if not item:
            return None
        venue = None
        primary_location = item.get("primary_location") or {}
        source = primary_location.get("source") or {}
        venue = source.get("display_name")
        return OpenAlexWork(
            work_id=item.get("id", ""),
            title=item.get("display_name", ""),
            doi=(item.get("doi") or "").removeprefix("https://doi.org/") or None,
            year=item.get("publication_year"),
            venue=venue,
            authors=item.get("authorships", []),
            raw=item,
        )
