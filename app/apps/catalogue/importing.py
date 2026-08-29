"""Own-catalogue import — reuses the scraping pipeline, writes OwnProduct.

The customer's own store is crawled like a competitor site (fetch → extract →
normalise) but persisted to OwnProduct/OwnListing and matched to canonical
Products. It is never registered as a Competitor.
"""
from __future__ import annotations

import hashlib
import logging

from django.conf import settings
from django.utils import timezone

from apps.matching.engine import match_own_product
from apps.scanning.scraping.adapters.registry import select_adapter
from apps.scanning.scraping.fetchers.http import HttpFetcher
from apps.scanning.scraping.orchestration import scrape_url

from .models import OwnCatalogueSource, OwnListing, OwnProduct, StockStatus

logger = logging.getLogger("rivaltracking.catalogue")


def _own_sku(normalized, url):
    if normalized.sku:
        return normalized.sku[:80]
    return "url-" + hashlib.sha256(url.encode("utf-8", "ignore")).hexdigest()[:16]


def upsert_own_product(workspace, normalized, url, *, source=None):
    """Create/update an OwnProduct (+ website OwnListing) and match it."""
    sku = _own_sku(normalized, url)
    own, _ = OwnProduct.objects.update_or_create(
        workspace=workspace,
        own_sku=sku,
        defaults={
            "name": normalized.title or sku,
            "brand": normalized.brand,
            "gtin": normalized.gtin,
            "ean": normalized.ean,
            "mpn": normalized.mpn,
            "category": normalized.category,
            "image_url": normalized.image_url,
            "our_price": normalized.price,
            "currency": normalized.currency,
            "in_stock": normalized.stock_status != StockStatus.OUT_OF_STOCK,
            "source": source,
        },
    )
    if url:
        OwnListing.objects.update_or_create(
            workspace=workspace,
            own_product=own,
            channel="website",
            defaults={"url": url[:500], "price": normalized.price, "currency": normalized.currency},
        )
    match_own_product(own)
    return own


def import_from_website(source, *, fetcher=None, throttle=True):
    """Crawl the workspace's own site and populate its catalogue."""
    own_fetcher = fetcher is None
    fetcher = fetcher or HttpFetcher()
    workspace = source.workspace
    now = timezone.now()
    source.status = OwnCatalogueSource.Status.IMPORTING
    source.save(update_fields=["status", "updated_at"])
    logger.info("catalogue.import.started source=%s url=%s", source.id, source.website_url)

    found, errors, error_messages = 0, 0, []
    try:
        home = fetcher.fetch(source.website_url)
        adapter = select_adapter(home)
        urls = adapter.discover(source, fetcher)[: settings.SCAN_MAX_PAGES]
        for url in urls:
            result, normalized = scrape_url(url, fetcher, adapter)
            if not result.ok:
                errors += 1
                error_messages.append(f"{url}: HTTP {result.status_code}")
                continue
            if normalized is None:
                continue
            upsert_own_product(workspace, normalized, url, source=source)
            found += 1
        if found and not errors:
            source.status = OwnCatalogueSource.Status.CONNECTED
        elif found:
            source.status = OwnCatalogueSource.Status.PARTIAL
        else:
            source.status = OwnCatalogueSource.Status.FAILED
            if not error_messages:
                error_messages.append("No products found at that URL.")
    except Exception as exc:  # a bad site never crashes the request/worker
        source.status = OwnCatalogueSource.Status.FAILED
        errors += 1
        error_messages.append(str(exc)[:200])
    finally:
        source.products_found = OwnProduct.objects.filter(
            workspace=workspace, source=source
        ).count()
        source.errors_count = errors
        source.error_summary = "\n".join(error_messages[:20])
        source.last_import_at = timezone.now()
        source.save()
        if own_fetcher:
            fetcher.close()
        logger.info(
            "catalogue.import.finished source=%s status=%s products=%s errors=%s",
            source.id, source.status, source.products_found, errors,
        )
    return source
