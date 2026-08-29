"""CSV own-catalogue import: auto-map headers, validate, upsert + match.

Upserts into the same OwnProduct/OwnListing models as the website import, so
comparison works identically regardless of source.
"""
from __future__ import annotations

import csv
import io

from apps.core.entities import slugify
from apps.matching.engine import match_own_product
from apps.scanning.scraping.normalizers.base import parse_price

from .models import OwnListing, OwnProduct

# Canonical field → accepted header names (lowercased).
HEADER_ALIASES = {
    "own_sku": ["sku", "own_sku", "product sku", "code", "id", "item"],
    "name": ["name", "title", "product", "product name", "product_name"],
    "url": ["url", "link", "product url", "product_url"],
    "our_price": ["price", "our price", "our_price", "selling price", "sale price"],
    "brand": ["brand", "manufacturer", "make"],
    "gtin": ["gtin", "gtin13", "barcode", "upc"],
    "ean": ["ean", "ean13"],
    "mpn": ["mpn", "manufacturer part number", "part number", "part_number"],
    "category": ["category", "type", "product type"],
    "currency": ["currency", "ccy"],
}


def _map_headers(fieldnames):
    lower = {(f or "").strip().lower(): f for f in fieldnames}
    mapping = {}
    for field, aliases in HEADER_ALIASES.items():
        for alias in aliases:
            if alias in lower:
                mapping[field] = lower[alias]
                break
    return mapping


def _val(row, mapping, field):
    col = mapping.get(field)
    return (row.get(col) or "").strip() if col else ""


def import_csv(workspace, uploaded_file, *, source=None):
    """Parse + upsert a product CSV. Returns a result dict for the UI."""
    try:
        text = uploaded_file.read().decode("utf-8-sig", errors="replace")
    except Exception:
        return {"error": "Could not read the file. Upload a UTF-8 CSV export."}

    reader = csv.DictReader(io.StringIO(text))
    mapping = _map_headers(reader.fieldnames or [])
    if "own_sku" not in mapping and "name" not in mapping:
        return {"error": "CSV needs at least a SKU or Name column."}

    imported, updated, errors = 0, 0, []
    for line, row in enumerate(reader, start=2):
        sku = _val(row, mapping, "own_sku")
        name = _val(row, mapping, "name")
        if not sku and not name:
            errors.append(f"Row {line}: missing both SKU and name.")
            continue
        sku = (sku or slugify(name))[:80]
        own, created = OwnProduct.objects.update_or_create(
            workspace=workspace,
            own_sku=sku,
            defaults={
                "name": name or sku,
                "brand": _val(row, mapping, "brand")[:120],
                "gtin": _val(row, mapping, "gtin")[:14],
                "ean": _val(row, mapping, "ean")[:14],
                "mpn": _val(row, mapping, "mpn")[:80],
                "category": _val(row, mapping, "category")[:120],
                "our_price": parse_price(_val(row, mapping, "our_price")),
                "currency": (_val(row, mapping, "currency") or "GBP")[:3].upper(),
                "source": source,
            },
        )
        url = _val(row, mapping, "url")
        if url:
            OwnListing.objects.update_or_create(
                workspace=workspace, own_product=own, channel="csv",
                defaults={"url": url[:500], "price": own.our_price, "currency": own.currency},
            )
        match_own_product(own)
        imported += 1 if created else 0
        updated += 0 if created else 1

    return {
        "imported": imported,
        "updated": updated,
        "errors": errors,
        "total": imported + updated,
        "mapped": sorted(mapping.keys()),
    }
