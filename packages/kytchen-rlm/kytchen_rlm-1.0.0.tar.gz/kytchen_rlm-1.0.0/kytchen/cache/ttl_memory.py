from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


def _now() -> float:
    return time.time()


@dataclass(slots=True)
class TTLMemoryCache(Generic[T]):
    _store: dict[str, tuple[float | None, T]] = field(default_factory=dict)

    def get(self, key: str) -> T | None:
        item = self._store.get(key)
        if item is None:
            return None
        expires_at, value = item
        if expires_at is not None and expires_at <= _now():
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: T, ttl_seconds: float | None = None) -> None:
        expires_at = None
        if ttl_seconds is not None and ttl_seconds > 0:
            expires_at = _now() + float(ttl_seconds)
        self._store[key] = (expires_at, value)

    def clear(self) -> None:
        self._store.clear()

    def prune(self) -> int:
        now = _now()
        removed = 0
        for k, (exp, _) in list(self._store.items()):
            if exp is not None and exp <= now:
                self._store.pop(k, None)
                removed += 1
        return removed
