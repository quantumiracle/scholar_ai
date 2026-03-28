from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any


@dataclass
class MemoryCache:
    ttl_seconds: int = 3600
    store: dict[str, tuple[float, Any]] = field(default_factory=dict)

    def get(self, key: str) -> Any | None:
        item = self.store.get(key)
        if not item:
            return None
        expires_at, value = item
        if expires_at < time():
            self.store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> Any:
        self.store[key] = (time() + self.ttl_seconds, value)
        return value
