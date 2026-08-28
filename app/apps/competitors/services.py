"""Competitor mutations against the mock store.

Each function notes the future backend endpoint it stands in for.
"""
import re

from apps.core.entities import slugify
from apps.core.mock.store import MockStore


def _row_from_url(url):
    """Port of services/competitors.ts addCompetitor(): derive a display name
    from the host and return an initialising CompetitorRow."""
    host = re.sub(r"^https?://", "", url.strip())
    host = re.sub(r"^www\.", "", host)
    host = re.sub(r"/.*$", "", host)
    stem = host.split(".")[0]
    stem = re.sub(r"[-_]", " ", stem).title().replace(" ", "")
    name = stem + (host[host.index(".") :] if "." in host else "")
    return {
        "slug": slugify(host),
        "name": name,
        "url": host,
        "market": "UK Toys",
        "products": 1824,
        "changes_today": None,
        "price_drops": None,
        "price_increases": None,
        "stock_changes": None,
        "last_scan": "Just now",
        "last_scan_minutes": 0,
        "status": "initialising",
        "added_at": "2026-08-28",
    }


def add_competitor(request, url):
    """Future: POST /api/competitors"""
    row = _row_from_url(url)
    store = MockStore(request)

    def _add(rows):
        if not any(c["slug"] == row["slug"] for c in rows):
            rows.append(row)

    store.mutate("competitors", _add)
    return row


def set_status(request, slug, status):
    """Future: PATCH /api/competitors/:id (pause/resume)"""

    def _set(rows):
        for c in rows:
            if c["slug"] == slug:
                c["status"] = status

    MockStore(request).mutate("competitors", _set)


def remove_competitor(request, slug):
    """Future: DELETE /api/competitors/:id"""
    store = MockStore(request)
    store.replace(
        "competitors", [c for c in store.get("competitors") if c["slug"] != slug]
    )


def save_monitoring_config(request, slug, config):
    """Future: PUT /api/competitors/:id/monitoring-config"""

    def _save(configs):
        configs[slug] = config

    MockStore(request).mutate("competitor_configs", _save)


DEFAULT_CONFIG = {
    "frequency": "Every 24 hours",
    "track_prices": True,
    "track_stock": True,
    "track_products": True,
    "track_promotions": True,
}


def get_monitoring_config(request, slug):
    configs = MockStore(request).get("competitor_configs")
    return {**DEFAULT_CONFIG, **configs.get(slug, {})}
