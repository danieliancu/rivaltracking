"""Default HTTP fetcher (httpx) with timeout, UA, retries and backoff."""
from __future__ import annotations

import time

import httpx
from django.conf import settings

from .base import Fetcher, FetchResult

RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class HttpFetcher(Fetcher):
    def __init__(self, timeout=None, user_agent=None, max_retries=None):
        self.timeout = timeout if timeout is not None else settings.HTTP_TIMEOUT
        self.user_agent = user_agent or settings.HTTP_USER_AGENT
        self.max_retries = (
            max_retries if max_retries is not None else settings.SCRAPER_MAX_RETRIES
        )
        self._client = httpx.Client(
            timeout=self.timeout,
            follow_redirects=True,
            headers={"User-Agent": self.user_agent, "Accept": "text/html,application/json;q=0.9,*/*;q=0.8"},
        )

    def fetch(self, url: str) -> FetchResult:
        last_error = ""
        for attempt in range(self.max_retries + 1):
            started = time.monotonic()
            try:
                resp = self._client.get(url)
            except httpx.HTTPError as exc:
                last_error = str(exc)
            else:
                elapsed = int((time.monotonic() - started) * 1000)
                if resp.status_code in RETRYABLE_STATUS and attempt < self.max_retries:
                    time.sleep(min(2 ** attempt, 8))
                    continue
                return FetchResult(
                    url=url,
                    status_code=resp.status_code,
                    text=resp.text,
                    final_url=str(resp.url),
                    headers=dict(resp.headers),
                    ok=resp.is_success,
                    elapsed_ms=elapsed,
                )
            if attempt < self.max_retries:
                time.sleep(min(2 ** attempt, 8))
        return FetchResult(url=url, status_code=0, ok=False, error=last_error)

    def close(self):
        self._client.close()
