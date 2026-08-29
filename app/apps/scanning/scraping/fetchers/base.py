"""Fetcher interface + result type.

HTTP is the default path; the browser fetcher is an optional escalation. The
orchestrator depends on this interface, so tests inject a fake fetcher and no
network is touched.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


@dataclass
class FetchResult:
    url: str
    status_code: int
    text: str = ""
    final_url: str = ""
    headers: dict = field(default_factory=dict)
    ok: bool = False
    error: str = ""
    elapsed_ms: int = 0

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8", "ignore")).hexdigest()


class Fetcher:
    """Fetch a URL and return a FetchResult. Never raises for HTTP errors."""

    def fetch(self, url: str) -> FetchResult:  # pragma: no cover - interface
        raise NotImplementedError

    def close(self):  # pragma: no cover - optional
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
