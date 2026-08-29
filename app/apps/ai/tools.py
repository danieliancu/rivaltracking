"""Retrieval tools over the ORM for Ask AI.

Every tool takes ``workspace`` and filters by it — AI answers can never reach
another tenant's data. Tools return small JSON-able structures (never raw pages
or unbounded record dumps).
"""
from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.catalogue import selectors as catalogue_selectors
from apps.catalogue.models import OwnProduct, Product, ProductListing
from apps.changes.models import ChangeEvent
from apps.competitors.models import Competitor


def get_recent_changes(workspace, *, days=7, limit=20):
    since = timezone.now() - timedelta(days=days)
    rows = (
        ChangeEvent.objects.for_workspace(workspace)
        .filter(detected_at__gte=since)
        .select_related("competitor", "product")
        .order_by("-detected_at")[:limit]
    )
    return [
        {
            "competitor": r.competitor.name,
            "product": r.product.name if r.product else "",
            "event": r.event_type,
            "previous": r.previous_value,
            "new": r.new_value,
            "impact": r.impact,
        }
        for r in rows
    ]


def compare_product_prices(workspace, *, product_slug):
    product = Product.objects.for_workspace(workspace).filter(slug=product_slug).first()
    if product is None:
        return {"product": product_slug, "listings": []}
    listings = (
        ProductListing.objects.filter(product=product, active=True)
        .select_related("competitor")
        .exclude(current_price=None)
    )
    return {
        "product": product.name,
        "listings": [
            {"competitor": l.competitor.name, "price": float(l.current_price), "in_stock": l.in_stock}
            for l in listings
        ],
    }


def get_competitor_summary(workspace, *, competitor_slug):
    c = Competitor.objects.for_workspace(workspace).filter(slug=competitor_slug).first()
    if c is None:
        return {}
    return {
        "name": c.name,
        "products": c.products_count,
        "changes_today": c.changes_today,
        "status": c.status,
    }


def get_market_position(workspace, *, own_sku):
    own = OwnProduct.objects.for_workspace(workspace).filter(own_sku=own_sku).first()
    if own is None:
        return {}
    return catalogue_selectors.price_position(own)


def search_products(workspace, *, query, limit=10):
    rows = (
        Product.objects.for_workspace(workspace)
        .filter(name__icontains=query)
        .values("name", "slug", "category")[:limit]
    )
    return list(rows)


def answer_context(workspace, question, context):
    """A compact bundle of structured facts for a free-form question."""
    return {
        "recent_changes": get_recent_changes(workspace, days=7, limit=10),
        "competitors": [
            {"name": c["name"], "products": c["products_count"]}
            for c in Competitor.objects.for_workspace(workspace).values("name", "products_count")
        ],
        "scope": context,
    }
