"""Site adapter base. Adapters may override discovery, product-URL rules and
extraction; the generic adapter implements the deterministic default path."""
from __future__ import annotations

from bs4 import BeautifulSoup

from ..discovery import patterns, sitemap
from ..extractors.base import ExtractedProduct
from ..extractors.dom import DomExtractor
from ..extractors.jsonld import JsonLdExtractor

# Extraction order: structured (JSON-LD) before DOM heuristics.
DEFAULT_EXTRACTORS = [JsonLdExtractor(), DomExtractor()]


class Adapter:
    name = "base"

    @staticmethod
    def detect(fetch_result) -> bool:  # pragma: no cover - overridden
        return False

    def extractors(self):
        return DEFAULT_EXTRACTORS

    def extract(self, fetch_result) -> ExtractedProduct | None:
        soup = BeautifulSoup(fetch_result.text, "html.parser")
        for extractor in self.extractors():
            product = extractor.extract(fetch_result, soup)
            if product and product.is_usable():
                return product
        return None

    def is_product_url(self, url: str) -> bool:
        return patterns.is_product_url(url)

    def discover(self, competitor, fetcher) -> list[str]:
        """Structured discovery first (sitemap), then category-link crawl."""
        urls = sitemap.sitemap_candidates(competitor, fetcher)
        if urls:
            return list(dict.fromkeys(urls))
        # Fallback: scan the homepage for product links.
        base = competitor.website_url or f"https://{competitor.domain}"
        host = competitor.domain or ""
        home = fetcher.fetch(base)
        if home.ok:
            return patterns.find_product_links(home.text, home.final_url or base, host)
        return []
