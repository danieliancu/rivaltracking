"""Deterministic normalisation: raw extracted strings → typed, canonical values.

Raw extracted values are preserved on the ExtractedProduct; normalisation
produces a separate NormalizedProduct so debugging and matching stay clean.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from apps.catalogue.models import StockStatus

_CURRENCY_SYMBOL = {"£": "GBP", "€": "EUR", "$": "USD", "lei": "RON"}
_IN_STOCK = {"instock", "in stock", "limitedavailability", "preorder", "onlineonly", "available"}
_OUT_STOCK = {"outofstock", "out of stock", "soldout", "sold out", "discontinued"}


@dataclass
class NormalizedProduct:
    title: str = ""
    brand: str = ""
    sku: str = ""
    gtin: str = ""
    ean: str = ""
    upc: str = ""
    mpn: str = ""
    price: Decimal | None = None
    sale_price: Decimal | None = None
    currency: str = "GBP"
    stock_status: str = StockStatus.UNKNOWN
    category: str = ""
    description: str = ""
    image_url: str = ""
    promotion: str = ""
    source_url: str = ""
    identifiers: dict = field(default_factory=dict)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def parse_price(value) -> Decimal | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float, Decimal)):
        try:
            return Decimal(str(value))
        except InvalidOperation:
            return None
    text = str(value).strip()
    # Keep digits, dot, comma; drop currency symbols/letters/spaces.
    text = re.sub(r"[^0-9.,]", "", text)
    if not text:
        return None
    # If both separators present, assume comma = thousands.
    if "," in text and "." in text:
        text = text.replace(",", "")
    elif text.count(",") == 1 and text.count(".") == 0:
        text = text.replace(",", ".")  # european decimal comma
    else:
        text = text.replace(",", "")
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def normalize_currency(currency: str, price_text: str = "") -> str:
    currency = (currency or "").strip().upper()
    if len(currency) == 3 and currency.isalpha():
        return currency
    for symbol, code in _CURRENCY_SYMBOL.items():
        if symbol in (price_text or "") or symbol in (currency or ""):
            return code
    return "GBP"


def normalize_stock(value: str) -> str:
    v = clean_text(value).lower()
    if not v:
        return StockStatus.UNKNOWN
    if v in _IN_STOCK or "in stock" in v or "instock" in v:
        return StockStatus.IN_STOCK
    if v in _OUT_STOCK or "out of stock" in v or "outofstock" in v or "sold out" in v:
        return StockStatus.OUT_OF_STOCK
    return StockStatus.UNKNOWN


def clean_identifier(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", (value or "")).upper()


def normalize(extracted) -> NormalizedProduct:
    price = parse_price(extracted.price)
    sale = parse_price(extracted.sale_price)
    gtin = clean_identifier(extracted.gtin or extracted.ean or extracted.upc)
    return NormalizedProduct(
        title=clean_text(extracted.title),
        brand=clean_text(extracted.brand),
        sku=clean_text(extracted.sku),
        gtin=gtin,
        ean=clean_identifier(extracted.ean) or gtin,
        upc=clean_identifier(extracted.upc),
        mpn=clean_text(extracted.mpn),
        price=price,
        sale_price=sale,
        currency=normalize_currency(extracted.currency, extracted.price),
        stock_status=normalize_stock(extracted.stock_status),
        category=clean_text(extracted.category),
        description=clean_text(extracted.description),
        image_url=(extracted.image_url or "").strip(),
        promotion=clean_text(extracted.promotion),
        source_url=(extracted.canonical_url or "").strip(),
        identifiers={
            k: v
            for k, v in {"gtin": gtin, "mpn": clean_text(extracted.mpn), "sku": clean_text(extracted.sku)}.items()
            if v
        },
    )
