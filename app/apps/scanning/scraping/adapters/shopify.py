"""Shopify adapter: detects Shopify storefronts. Extraction uses the default
JSON-LD/DOM pipeline (Shopify emits schema.org Product); discovery can use the
Shopify sitemap which the generic sitemap discovery already handles."""
from .base import Adapter


class ShopifyAdapter(Adapter):
    name = "shopify"

    @staticmethod
    def detect(fetch_result) -> bool:
        text = fetch_result.text or ""
        return "cdn.shopify.com" in text or "Shopify.theme" in text or "/cdn/shop/" in text
