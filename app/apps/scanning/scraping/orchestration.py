"""Scan orchestrator: discovery → fetch → extract → normalise (+ evidence).

Listing persistence, snapshots and change detection are attached in the next
commit via ``persist_hook``. Everything here is deterministic and fetcher-
injectable, so tests drive the whole pipeline from HTML fixtures with no network.
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from datetime import timedelta
from urllib.parse import urlparse

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .adapters.registry import select_adapter
from .fetchers.http import HttpFetcher
from .normalizers.base import normalize


@dataclass
class ScrapedItem:
    url: str
    normalized: object  # NormalizedProduct
    fetch_result: object


@dataclass
class ScanOutcome:
    pages_requested: int = 0
    products_found: int = 0
    errors: int = 0
    items: list = field(default_factory=list)
    error_messages: list = field(default_factory=list)
    blocked: bool = False
    block_reason: str = ""


def _looks_blocked(result):
    """True when a fetch was *refused* by anti-bot protection (Cloudflare/WAF)
    rather than simply missing — so we can tell the user the site is protected
    instead of implying it has no products.

    Refusal is judged by HTTP status only. A 200 OK page is never "blocked" even
    if its markup happens to contain words like "cloudflare" or "captcha"
    (CDN scripts, contact forms, etc. commonly do) — that was a false positive.
    A Cloudflare interstitial is served with a 403/503, which this catches."""
    if result is None:
        return False
    if result.status_code in (401, 403, 429, 503):
        return True
    # Some WAFs (e.g. AWS WAF) serve a JS challenge with HTTP 202 instead of a
    # refusal code. 202 for a page GET is already abnormal, so gate on explicit
    # challenge markers to stay clear of the 200-OK false positive.
    if result.status_code == 202:
        body = (getattr(result, "text", "") or "").lower()
        return any(
            m in body
            for m in ("awswaf", "gokuprops", "challenge-platform", "px-captcha", "captcha")
        )
    return False


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8", "ignore")).hexdigest()


def _throttle(host: str, rps: float):
    if rps <= 0:
        return
    key = f"ratelimit:{host}"
    min_gap = 1.0 / rps
    while True:
        if cache.add(key, "1", timeout=max(1, int(min_gap) or 1)):
            return
        time.sleep(min_gap)


def _base_url(competitor):
    return competitor.website_url or f"https://{competitor.domain}"


def scrape_url(url, fetcher, adapter=None):
    """Fetch one URL and return (fetch_result, normalized|None)."""
    result = fetcher.fetch(url)
    if not result.ok or not result.text:
        return result, None
    adapter = adapter or select_adapter(result)
    extracted = adapter.extract(result)
    if extracted is None:
        return result, None
    if not extracted.canonical_url:
        extracted.canonical_url = result.final_url or url
    return result, normalize(extracted)


def run_competitor_scan(competitor, *, fetcher=None, job=None, throttle=True, persist_hook=None):
    """Discover product URLs, scrape each, record evidence, return a ScanOutcome.

    ``persist_hook(competitor, items, job)`` (added next commit) turns scraped
    items into listings/snapshots/changes; when None, only discovery + evidence
    are recorded.
    """
    from apps.scanning.models import DiscoveredUrl, RawCapture

    own_fetcher = fetcher is None
    fetcher = fetcher or HttpFetcher()
    outcome = ScanOutcome()
    host = competitor.domain or urlparse(_base_url(competitor)).netloc
    rps = settings.SCRAPER_PER_DOMAIN_RPS
    now = timezone.now()
    retained_until = now + timedelta(days=settings.RAW_CAPTURE_RETENTION_DAYS)

    try:
        home = fetcher.fetch(_base_url(competitor))
        if _looks_blocked(home):
            outcome.blocked = True
            outcome.block_reason = (
                f"Site refused automated access (HTTP {home.status_code}); "
                "it is protected by anti-bot software (e.g. Cloudflare)."
            )
            outcome.errors += 1
            outcome.error_messages.append(outcome.block_reason)
            return outcome
        adapter = select_adapter(home)
        urls = adapter.discover(competitor, fetcher)[: settings.SCAN_MAX_PAGES]

        for url in urls:
            DiscoveredUrl.objects.update_or_create(
                workspace=competitor.workspace,
                competitor=competitor,
                url_hash=_url_hash(url),
                defaults={
                    "url": url[:800],
                    "kind": DiscoveredUrl.Kind.PRODUCT,
                    "status": DiscoveredUrl.Status.ACTIVE,
                    "last_seen_at": now,
                },
            )
            if throttle:
                _throttle(host, rps)
            result, normalized = scrape_url(url, fetcher, adapter)
            outcome.pages_requested += 1
            if not result.ok:
                outcome.errors += 1
                outcome.error_messages.append(f"{url}: HTTP {result.status_code} {result.error}".strip())
                DiscoveredUrl.objects.filter(
                    workspace=competitor.workspace, competitor=competitor, url_hash=_url_hash(url)
                ).update(status=DiscoveredUrl.Status.FAILED)
                continue
            RawCapture.objects.create(
                workspace=competitor.workspace,
                scan_job=job,
                competitor=competitor,
                url=url[:800],
                http_status=result.status_code,
                content_hash=result.content_hash,
                extraction=_capture_payload(normalized),
                snippet=result.text[:500],
                retained_until=retained_until,
            )
            if normalized is not None:
                outcome.products_found += 1
                outcome.items.append(ScrapedItem(url=url, normalized=normalized, fetch_result=result))
    finally:
        if own_fetcher:
            fetcher.close()

    # Home was reachable but the product pages were refused wholesale — also a
    # protected site, not an empty one.
    if not outcome.blocked and outcome.pages_requested and outcome.products_found == 0:
        refused = sum(
            1
            for m in outcome.error_messages
            if any(code in m for code in ("HTTP 403", "HTTP 429", "HTTP 503", "HTTP 401"))
        )
        if refused and refused >= outcome.pages_requested * 0.8:
            outcome.blocked = True
            outcome.block_reason = "Product pages refused automated access (anti-bot)."

    if persist_hook is not None:
        persist_hook(competitor, outcome.items, job)
    return outcome


def _capture_payload(normalized):
    if normalized is None:
        return {}
    return {
        "title": normalized.title,
        "price": str(normalized.price) if normalized.price is not None else None,
        "currency": normalized.currency,
        "stock_status": normalized.stock_status,
        "gtin": normalized.gtin,
        "sku": normalized.sku,
        "source_url": normalized.source_url,
    }
