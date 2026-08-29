"""Deterministic product-URL heuristics + link discovery."""
from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

PRODUCT_URL_HINTS = re.compile(r"/(product|products|p|item|dp|shop)/", re.IGNORECASE)
NON_PRODUCT_HINTS = re.compile(
    r"/(cart|checkout|account|login|search|blog|about|contact|policies|pages)/",
    re.IGNORECASE,
)


def is_product_url(url: str) -> bool:
    path = urlparse(url).path
    if NON_PRODUCT_HINTS.search(path):
        return False
    return bool(PRODUCT_URL_HINTS.search(path))


def same_host(url: str, host: str) -> bool:
    netloc = urlparse(url).netloc.lower().lstrip("www.")
    return netloc.endswith(host.lower().lstrip("www."))


def find_product_links(html: str, base_url: str, host: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    found = []
    seen = set()
    for a in soup.find_all("a", href=True):
        url = urljoin(base_url, a["href"].split("#")[0])
        if url in seen:
            continue
        seen.add(url)
        if same_host(url, host) and is_product_url(url):
            found.append(url)
    return found
