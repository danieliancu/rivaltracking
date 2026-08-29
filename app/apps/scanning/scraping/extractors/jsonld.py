"""JSON-LD / schema.org Product extractor (the preferred, structured path)."""
from __future__ import annotations

import json

from .base import ExtractedProduct, Extractor


def _iter_jsonld_objects(soup):
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = tag.string or tag.get_text() or ""
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            continue
        stack = [data]
        while stack:
            item = stack.pop()
            if isinstance(item, list):
                stack.extend(item)
            elif isinstance(item, dict):
                if "@graph" in item and isinstance(item["@graph"], list):
                    stack.extend(item["@graph"])
                yield item


def _types(obj):
    t = obj.get("@type", "")
    return {t} if isinstance(t, str) else set(t or [])


def _first(value):
    return value[0] if isinstance(value, list) and value else value


def _brand(value):
    value = _first(value)
    if isinstance(value, dict):
        return value.get("name", "")
    return value or ""


def _offer_fields(product):
    offers = _first(product.get("offers")) or {}
    if not isinstance(offers, dict):
        offers = {}
    availability = str(offers.get("availability", "")).rsplit("/", 1)[-1]
    return {
        "price": str(offers.get("price", "") or offers.get("lowPrice", "") or ""),
        "currency": offers.get("priceCurrency", "") or "",
        "stock_status": availability,
    }


class JsonLdExtractor(Extractor):
    method = "jsonld"

    def extract(self, fetch_result, soup=None) -> ExtractedProduct | None:
        if soup is None:
            return None
        for obj in _iter_jsonld_objects(soup):
            if "Product" not in _types(obj):
                continue
            offer = _offer_fields(obj)
            image = _first(obj.get("image"))
            if isinstance(image, dict):
                image = image.get("url", "")
            return ExtractedProduct(
                title=str(obj.get("name", "")).strip(),
                brand=_brand(obj.get("brand")),
                sku=str(obj.get("sku", "")),
                gtin=str(obj.get("gtin13") or obj.get("gtin") or ""),
                ean=str(obj.get("gtin13") or obj.get("ean") or ""),
                mpn=str(obj.get("mpn", "")),
                price=offer["price"],
                currency=offer["currency"],
                stock_status=offer["stock_status"],
                category=str(obj.get("category", "")),
                description=str(obj.get("description", ""))[:2000],
                image_url=image or "",
                canonical_url=str(obj.get("url") or fetch_result.final_url or fetch_result.url),
                source_method=self.method,
                raw={"jsonld_type": "Product"},
            )
        return None
