"""Optional Playwright browser fetcher (escalation for JS-rendered pages).

Deferred by default: Playwright is not installed in the standard image. Enable
with BROWSER_ENABLED=1 on a dedicated worker built from requirements/browser.txt
(`playwright install chromium`). The interface is identical to HttpFetcher so
the orchestrator can escalate transparently.
"""
from __future__ import annotations

import time

from django.conf import settings

from .base import Fetcher, FetchResult


class BrowserUnavailable(RuntimeError):
    pass


class BrowserFetcher(Fetcher):
    def __init__(self, timeout=None, user_agent=None):
        if not settings.BROWSER_ENABLED:
            raise BrowserUnavailable("BROWSER_ENABLED is off.")
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401
        except ImportError as exc:  # pragma: no cover - optional dep
            raise BrowserUnavailable(
                "Playwright is not installed (see requirements/browser.txt)."
            ) from exc
        self.timeout = timeout if timeout is not None else settings.HTTP_TIMEOUT
        self.user_agent = user_agent or settings.HTTP_USER_AGENT

    def fetch(self, url: str) -> FetchResult:  # pragma: no cover - needs browser
        from playwright.sync_api import sync_playwright

        started = time.monotonic()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=self.user_agent)
            try:
                resp = page.goto(url, timeout=self.timeout * 1000, wait_until="domcontentloaded")
                html = page.content()
                status = resp.status if resp else 0
                return FetchResult(
                    url=url,
                    status_code=status,
                    text=html,
                    final_url=page.url,
                    ok=bool(resp and resp.ok),
                    elapsed_ms=int((time.monotonic() - started) * 1000),
                )
            finally:
                browser.close()
