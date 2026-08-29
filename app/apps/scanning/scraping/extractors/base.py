"""Extracted-product type + the extraction pipeline.

Extraction priority (deterministic; AI is never used here):
  1. JSON-LD / schema.org Product
  2. embedded structured state (adapter-specific)
  3. DOM selectors / OpenGraph
  4. site adapter overrides
  5. generic fallback
The first extractor that yields a usable product wins.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExtractedProduct:
    title: str = ""
    brand: str = ""
    sku: str = ""
    gtin: str = ""
    ean: str = ""
    upc: str = ""
    mpn: str = ""
    price: str = ""
    sale_price: str = ""
    currency: str = ""
    stock_status: str = ""
    stock_quantity: str = ""
    category: str = ""
    description: str = ""
    image_url: str = ""
    promotion: str = ""
    canonical_url: str = ""
    identifiers: dict = field(default_factory=dict)
    variants: list = field(default_factory=list)
    source_method: str = ""
    raw: dict = field(default_factory=dict)

    def is_usable(self) -> bool:
        return bool(self.title) and bool(
            self.price or self.sale_price or self.gtin or self.ean or self.sku
        )


class Extractor:
    method = "base"

    def extract(self, fetch_result, soup=None) -> ExtractedProduct | None:  # pragma: no cover
        raise NotImplementedError
