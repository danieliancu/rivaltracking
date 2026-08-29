"""Own-catalogue price-position metrics — deterministic business maths (no AI).

Given an OwnProduct matched to a canonical Product, compare our price against
the competitor ProductListings for that same product.
"""
from __future__ import annotations

import statistics

from .models import OwnProduct, ProductListing, StockStatus


def _competitor_prices(product):
    return [
        float(p)
        for p in ProductListing.objects.filter(product=product, active=True)
        .exclude(current_price=None)
        .values_list("current_price", flat=True)
    ]


def price_position(own_product):
    """Return our price vs the competitor market for the matched product."""
    product = own_product.product
    prices = _competitor_prices(product) if product else []
    our = float(own_product.our_price) if own_product.our_price is not None else None
    data = {
        "own_product": own_product.name,
        "our_price": our,
        "competitors": len(prices),
        "lowest": min(prices) if prices else None,
        "highest": max(prices) if prices else None,
        "median": round(statistics.median(prices), 2) if prices else None,
        "average": round(statistics.fmean(prices), 2) if prices else None,
        "position": None,
        "diff_vs_lowest_pct": None,
        "in_stock_competitors": ProductListing.objects.filter(
            product=product, active=True, current_stock_status=StockStatus.IN_STOCK
        ).count()
        if product
        else 0,
    }
    if our is not None and prices:
        lowest = data["lowest"]
        if our < lowest:
            data["position"] = "cheapest"
        elif our > data["highest"]:
            data["position"] = "most_expensive"
        else:
            data["position"] = "mid_market"
        if lowest:
            data["diff_vs_lowest_pct"] = round((our - lowest) / lowest * 100, 1)
    return data


def workspace_price_positions(workspace):
    return [
        price_position(op)
        for op in OwnProduct.objects.for_workspace(workspace).select_related("product")
    ]


def catalogue_gaps(workspace):
    """Canonical products competitors sell that we don't have in our catalogue."""
    own_product_ids = set(
        OwnProduct.objects.for_workspace(workspace)
        .exclude(product=None)
        .values_list("product_id", flat=True)
    )
    from .models import Product

    gaps = (
        Product.objects.for_workspace(workspace)
        .filter(listings__active=True)
        .exclude(id__in=own_product_ids)
        .distinct()
    )
    return gaps


def unmatched_own_products(workspace):
    """Own products we sell that no competitor lists (matched product has no
    active competitor listings)."""
    from .models import OwnProduct

    result = []
    for op in OwnProduct.objects.for_workspace(workspace).select_related("product"):
        if op.product is None or not ProductListing.objects.filter(
            product=op.product, active=True
        ).exists():
            result.append(op)
    return result


def own_position_summary(workspace):
    """Headline own-vs-market counts for the Overview (all zero when empty)."""
    positions = [p for p in workspace_price_positions(workspace) if p["our_price"] is not None and p["competitors"]]
    return {
        "matched": len(positions),
        "cheapest": sum(1 for p in positions if p["position"] == "cheapest"),
        "most_expensive": sum(1 for p in positions if p["position"] == "most_expensive"),
        "gaps": catalogue_gaps(workspace).count(),
        "unmatched": len(unmatched_own_products(workspace)),
    }
