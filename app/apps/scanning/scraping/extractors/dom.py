"""Generic DOM / OpenGraph fallback extractor (last resort, deterministic)."""
from __future__ import annotations

from .base import ExtractedProduct, Extractor


def _meta(soup, **attrs):
    tag = soup.find("meta", attrs=attrs)
    return (tag.get("content") or "").strip() if tag else ""


def _itemprop(soup, name):
    tag = soup.find(attrs={"itemprop": name})
    if not tag:
        return ""
    return (tag.get("content") or tag.get_text() or "").strip()


class DomExtractor(Extractor):
    method = "dom"

    def extract(self, fetch_result, soup=None) -> ExtractedProduct | None:
        if soup is None:
            return None
        title = (
            _meta(soup, property="og:title")
            or _itemprop(soup, "name")
            or (soup.title.get_text().strip() if soup.title else "")
        )
        price = (
            _meta(soup, property="product:price:amount")
            or _itemprop(soup, "price")
        )
        currency = _meta(soup, property="product:price:currency") or _itemprop(soup, "priceCurrency")
        availability = (
            _meta(soup, property="product:availability")
            or _itemprop(soup, "availability")
        )
        product = ExtractedProduct(
            title=title,
            brand=_meta(soup, property="product:brand") or _itemprop(soup, "brand"),
            sku=_itemprop(soup, "sku"),
            price=price,
            currency=currency,
            stock_status=availability,
            description=_meta(soup, property="og:description")[:2000],
            image_url=_meta(soup, property="og:image"),
            canonical_url=(
                (soup.find("link", rel="canonical") or {}).get("href", "")
                if soup.find("link", rel="canonical")
                else fetch_result.final_url or fetch_result.url
            ),
            source_method=self.method,
        )
        return product if product.title else None
