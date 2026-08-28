"""Product reads over the mock store: table state, chart payloads, compare data."""
import json

from apps.changes import selectors as change_selectors
from apps.competitors import selectors as competitor_selectors
from apps.core.entities import category_param, slugify
from apps.core.mock.store import MockStore
from apps.core.selectors import paginate, to_int

from . import filters
from .data import ACTIVE_CATEGORIES, FILTER_OPTIONS, PRICE_MOVEMENT, PRODUCT_KPIS, SORT_OPTIONS

# products.tsx kpiIcons — id → lucide glyph.
KPI_ICONS = {
    "total": "package",
    "new": "sparkles",
    "price": "tags",
    "stock": "package-x",
    "removed": "trash-2",
}


def all_rows(request):
    return MockStore(request).get("products")


def by_slug(request, slug):
    for row in all_rows(request):
        if row["slug"] == slug:
            return row
    return None


def watchlist(request):
    return MockStore(request).get("watchlist")


def kpi_cards():
    return [
        {"icon": KPI_ICONS.get(k["id"], "package"), "tone": k["tone"], "value": k["value"], "label": k["label"]}
        for k in PRODUCT_KPIS
    ]


def price_movement_card():
    """products/price-movement.tsx — legend counts + line chart payload."""
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
    return {
        "competitors": [{"value": "", "label": FILTER_OPTIONS["competitors"][0]}]
        + [
            {"value": competitor_selectors.slug_for(request, name) or slugify(name), "label": name}
            for name in FILTER_OPTIONS["competitors"][1:]
        ],
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
    """Current filter state expressed as the select values (URL tokens)."""
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
    """Everything the products-table fragment needs (filter → sort → paginate).

    `locked_competitor` (slug) pre-filters rows and hides the competitor select
    — embedded mode on the competitor detail page.
    """
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
    lowest = min(listing["price"] for listing in matched["listings"])
    listings = [{**listing, "is_lowest": listing["price"] == lowest} for listing in matched["listings"]]
    return {
        "matched": matched,
        "listings": listings,
        "lowest_out_of_stock": any(l["is_lowest"] and not l["in_stock"] for l in listings),
    }
