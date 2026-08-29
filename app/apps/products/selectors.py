"""Product reads over the ORM: table state, chart payloads, compare data.

The flat products table shows one row per canonical Product, represented by its
primary ProductListing. ``product_dict`` rebuilds the exact Phase 1 product dict
(including the optional ``matched`` block) so the templates are unchanged. The
pure filter/sort/paginate helpers in filters.py then run over those dicts; a
single query + prefetch keeps this free of N+1s at the current catalogue size.
"""
import json

from django.db.models import Prefetch
from django.utils import timezone

from apps.catalogue.models import Product, ProductListing, StockStatus
from apps.changes import selectors as change_selectors
from apps.competitors import selectors as competitor_selectors
from apps.core.entities import category_param, slugify
from apps.core.format import relative_time
from apps.core.selectors import paginate, to_int

from . import filters
from .data import ACTIVE_CATEGORIES, FILTER_OPTIONS, PRICE_MOVEMENT, PRODUCT_KPIS, SORT_OPTIONS
from .models import WatchlistItem

KPI_ICONS = {
    "total": "package",
    "new": "sparkles",
    "price": "tags",
    "stock": "package-x",
    "removed": "trash-2",
}


def _workspace(request):
    return getattr(request, "workspace", None)


def _minutes_since(dt, now):
    if dt is None:
        return None
    return max(0, int((now - dt).total_seconds() // 60))


def _price(value):
    return None if value is None else float(value)


def _matched_listing(listing, now):
    return {
        "competitor": listing.competitor.name,
        "price": _price(listing.current_price),
        "in_stock": listing.in_stock,
        "promotion": listing.current_promotion or None,
        "last_scan": relative_time(_minutes_since(listing.competitor.last_scan_at, now)),
    }


def product_dict(product, primary, listings, now):
    """Canonical Product + primary listing → the Phase 1 product dict."""
    minutes = _minutes_since(primary.last_change_at, now)
    row = {
        "slug": product.slug,
        "name": product.name,
        "sku": product.sku,
        "tone": product.tone,
        "competitor": primary.competitor.name,
        "category": product.category,
        "current_price": _price(primary.current_price),
        "previous_price": _price(primary.previous_price),
        "change": {"kind": primary.change_kind, "label": primary.change_label},
        "in_stock": primary.in_stock,
        "last_change": relative_time(minutes),
        "last_change_minutes": minutes if minutes is not None else 0,
        "discovered_at": primary.first_seen_at.date().isoformat() if primary.first_seen_at else "",
        "source_url": primary.source_url,
        "image": product.image_url or None,
    }
    if len(listings) > 1 or product.match_confidence:
        row["matched"] = {
            "count": len(listings),
            "confidence": product.match_confidence,
            "insight": product.match_insight,
            "listings": [_matched_listing(m, now) for m in listings],
        }
    return row


def _products_qs(request):
    return (
        Product.objects.for_workspace(_workspace(request))
        .prefetch_related(
            Prefetch(
                "listings",
                queryset=ProductListing.objects.select_related("competitor"),
            )
        )
    )


def _row_from_product(product, now):
    listings = list(product.listings.all())
    if not listings:
        return None
    primary = next((m for m in listings if m.is_primary), listings[0])
    return product_dict(product, primary, listings, now)


def all_rows(request):
    now = timezone.now()
    rows = []
    for product in _products_qs(request):
        row = _row_from_product(product, now)
        if row is not None:
            rows.append(row)
    return rows


def by_slug(request, slug):
    product = _products_qs(request).filter(slug=slug).first()
    if product is None:
        return None
    return _row_from_product(product, timezone.now())


def watchlist(request):
    return list(
        WatchlistItem.objects.for_workspace(_workspace(request)).values_list(
            "product__slug", flat=True
        )
    )


def kpi_cards(request):
    ws = _workspace(request)
    primary = ProductListing.objects.for_workspace(ws).filter(is_primary=True)
    values = {
        "total": Product.objects.for_workspace(ws).count(),
        "new": primary.filter(change_kind="new").count(),
        "price": primary.filter(change_kind__in=["drop", "increase"]).count(),
        "stock": primary.filter(change_kind__in=["oos", "back"]).count(),
        "removed": primary.filter(change_kind="removed").count(),
    }
    return [
        {
            "icon": KPI_ICONS.get(k["id"], "package"),
            "tone": k["tone"],
            "value": f"{values.get(k['id'], 0):,}",
            "label": k["label"],
        }
        for k in PRODUCT_KPIS
    ]


def price_movement_card():
    """products/price-movement.tsx — legend counts + line chart payload.

    Presentational analytics (headline chart); the real time series is a Phase 3
    aggregation. Kept from the deterministic seed so the chart stays populated.
    """
    series = PRICE_MOVEMENT["series"]
    return {
        "decreases": PRICE_MOVEMENT["decreases"],
        "increases": PRICE_MOVEMENT["increases"],
        "chart": {
            "type": "line",
            "labels": [p["date"] for p in series],
            "series": [
                {"label": "Price decreases", "data": [p["decreases"] for p in series], "color": "success"},
                {"label": "Price increases", "data": [p["increases"] for p in series], "color": "destructive", "dashed": True},
            ],
            "options": {},
        },
    }


def active_categories_chart():
    """products/active-categories.tsx — horizontal bars with value labels."""
    return {
        "type": "hbar",
        "labels": [c["name"] for c in ACTIVE_CATEGORIES],
        "series": [{"data": [c["changes"] for c in ACTIVE_CATEGORIES], "color": "chart-1"}],
        "options": {"labels": True, "barSize": 16, "labelWidth": 112},
    }


def filter_options(request):
    """Select option lists whose values are the URL param tokens ("" = default)."""
    competitors = [{"value": "", "label": "All competitors"}] + [
        {"value": c["slug"], "label": c["name"]}
        for c in competitor_selectors.header_list(request)
    ]
    return {
        "competitors": competitors,
        "categories": [{"value": "", "label": FILTER_OPTIONS["categories"][0]}]
        + [{"value": category_param(name), "label": name} for name in FILTER_OPTIONS["categories"][1:]],
        "change_types": FILTER_OPTIONS["change_types"],
        "stock": FILTER_OPTIONS["stock"],
        "date_ranges": [
            {"value": filters.RANGE_PARAM_BY_LABEL.get(label, "custom"), "label": label}
            for label in FILTER_OPTIONS["date_ranges"]
        ],
        "sorts": SORT_OPTIONS,
    }


def selected_tokens(state_filters, sort):
    return {
        "competitor": ""
        if state_filters["competitor"] == filters.DEFAULT_FILTERS["competitor"]
        else slugify(state_filters["competitor"]),
        "category": ""
        if state_filters["category"] == filters.DEFAULT_FILTERS["category"]
        else category_param(state_filters["category"]),
        "change": state_filters["change_type"],
        "stock": state_filters["stock"],
        "range": filters.RANGE_PARAM_BY_LABEL.get(state_filters["date_range"], "custom"),
        "sort": sort,
    }


def table_state(request, params, locked_competitor=None, preselected=None):
    """Everything the products-table fragment needs (filter → sort → paginate)."""
    rows = all_rows(request)
    locked_name = (
        competitor_selectors.name_for(request, locked_competitor) if locked_competitor else None
    )
    if locked_name:
        rows = [r for r in rows if r["competitor"] == locked_name]

    state_filters = filters.filters_from_params(
        params, lambda slug: competitor_selectors.name_for(request, slug)
    )
    sort_param = params.get("sort")
    sort = sort_param if filters.is_valid_sort(sort_param) else "recent"
    page_num = max(1, to_int(params.get("page"), 1))

    visible = filters.sort_products(filters.filter_products(rows, state_filters), sort)
    page = paginate(visible, page_num, filters.PAGE_SIZE)
    canonical_qs = filters.canonical_query(
        state_filters,
        sort,
        page["page"],
        lambda name: competitor_selectors.slug_for(request, name) or slugify(name),
    )
    return {
        "filters": state_filters,
        "sort": sort,
        "page": page,
        "has_rows": bool(rows),
        "has_visible": bool(visible),
        "active_filters": filters.active_filter_count(state_filters, locked=bool(locked_name)),
        "canonical_qs": canonical_qs,
        "selected": selected_tokens(state_filters, sort),
        "watchlist": watchlist(request),
        "locked_competitor": locked_name,
        "locked_slug": locked_competitor if locked_name else None,
        "page_slugs_json": json.dumps([r["slug"] for r in page["rows"]]),
        "preselected_json": json.dumps(list(preselected or [])),
    }


def events_for(request, slug):
    """product-details.tsx: change events for one product slug."""
    return [e for e in change_selectors.all_events(request) if e["product"]["slug"] == slug]


def events_by_kinds(events, kinds):
    return [e for e in events if e["kind"] in kinds]


def compare_context(product):
    """products/compare-drawer.tsx — listings with lowest-price flags."""
    matched = product.get("matched") if product else None
    if not matched:
        return None
    prices = [l["price"] for l in matched["listings"] if l["price"] is not None]
    lowest = min(prices) if prices else None
    listings = [
        {**listing, "is_lowest": listing["price"] == lowest} for listing in matched["listings"]
    ]
    return {
        "matched": matched,
        "listings": listings,
        "lowest_out_of_stock": any(l["is_lowest"] and not l["in_stock"] for l in listings),
    }
