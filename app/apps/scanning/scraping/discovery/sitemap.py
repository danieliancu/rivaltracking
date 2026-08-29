"""Sitemap-based catalogue discovery (structured, deterministic — tried first)."""
from __future__ import annotations

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .patterns import is_product_url

_MAX_SITEMAPS = 20


def _base(competitor):
    domain = competitor.domain or urlparse(competitor.website_url).netloc
    return f"https://{domain.lstrip('www.')}"


def _locs(xml_text: str) -> list[str]:
    soup = BeautifulSoup(xml_text, "xml")
    return [loc.get_text().strip() for loc in soup.find_all("loc") if loc.get_text().strip()]


def sitemap_candidates(competitor, fetcher) -> list[str]:
    """Return product-like URLs discovered from sitemap.xml (+ nested indexes)."""
    base = _base(competitor)
    to_visit = [f"{base}/sitemap.xml"]
    # robots.txt may list additional sitemaps.
    robots = fetcher.fetch(f"{base}/robots.txt")
    if robots.ok:
        to_visit += re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots.text)

    seen_sitemaps = set()
    product_urls: list[str] = []
    while to_visit and len(seen_sitemaps) < _MAX_SITEMAPS:
        sm = to_visit.pop(0)
        if sm in seen_sitemaps:
            continue
        seen_sitemaps.add(sm)
        result = fetcher.fetch(sm)
        if not result.ok:
            continue
        locs = _locs(result.text)
        for loc in locs:
            if loc.endswith(".xml") or "sitemap" in loc.lower():
                to_visit.append(loc)
            elif is_product_url(loc):
                product_urls.append(loc)
    return product_urls
