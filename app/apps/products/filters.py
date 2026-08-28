"""Pure product filtering, sorting and CSV assembly.

Faithful port of prototype-react/src/lib/product-filters.ts plus the sorters,
PAGE_SIZE and range-param map from components/products/products-table.tsx.
The backend will eventually do this server-side (GET /api/products?...).
"""
from urllib.parse import urlencode

from apps.core.entities import category_from_param, category_param, slugify

from .data import FILTER_OPTIONS

PAGE_SIZE = 8

DEFAULT_FILTERS = {
    "query": "",
    "competitor": FILTER_OPTIONS["competitors"][0],
    "category": FILTER_OPTIONS["categories"][0],
    "change_type": "all",
    "stock": "all",
    "date_range": "30 days",
}

# Query-param tokens (spec-level, e.g. "price-decrease") → ChangeKind.
KIND_BY_PARAM = {
    "new": "new",
    "price-decrease": "drop",
    "drop": "drop",
    "price-increase": "increase",
    "increase": "increase",
    "out-of-stock": "oos",
    "oos": "oos",
    "back-in-stock": "back",
    "back": "back",
    "removed": "removed",
    "promotion-started": "promo",
    "promo": "promo",
    "name": "name",
    "category": "category",
}


def kind_from_param(param):
    if not param:
        return "all"
    return KIND_BY_PARAM.get(param.lower(), "all")


RANGE_LABEL_BY_PARAM = {"today": "Today", "7d": "7 days", "30d": "30 days"}


def range_label_from_param(param):
    return RANGE_LABEL_BY_PARAM.get(param.lower()) if param else None


RANGE_MINUTES_BY_LABEL = {"Today": 24 * 60, "7 days": 7 * 24 * 60, "30 days": 30 * 24 * 60}

# products-table.tsx rangeParamByLabel ("Custom" has no URL token).
RANGE_PARAM_BY_LABEL = {"Today": "today", "7 days": "7d", "30 days": "30d"}


def filters_from_params(params, competitor_name_for_slug):
    """productFiltersFromParams — URL → filter state, so deep links pre-filter."""
    competitor_slug = params.get("competitor")
    category = params.get("category")
    stock = params.get("stock") or ""
    return {
        "query": params.get("q") or "",
        "competitor": (competitor_slug and competitor_name_for_slug(competitor_slug))
        or DEFAULT_FILTERS["competitor"],
        "category": (category and category_from_param(category, FILTER_OPTIONS["categories"]))
        or DEFAULT_FILTERS["category"],
        "change_type": kind_from_param(params.get("change")),
        "stock": stock if stock in ("in", "out") else "all",
        "date_range": range_label_from_param(params.get("range")) or DEFAULT_FILTERS["date_range"],
    }


def filter_products(rows, f):
    q = f["query"].strip().lower()
    max_minutes = RANGE_MINUTES_BY_LABEL.get(f["date_range"])
    return [
        r
        for r in rows
        if (
            not q
            or q in r["name"].lower()
            or q in r["sku"].lower()
            or q in r["category"].lower()
        )
        and (f["competitor"] == DEFAULT_FILTERS["competitor"] or r["competitor"] == f["competitor"])
        and (f["category"] == DEFAULT_FILTERS["category"] or r["category"] == f["category"])
        and (f["change_type"] == "all" or r["change"]["kind"] == f["change_type"])
        and (f["stock"] == "all" or (r["in_stock"] if f["stock"] == "in" else not r["in_stock"]))
        and (max_minutes is None or r["last_change_minutes"] <= max_minutes)
    ]


def price_delta(p):
    if p["previous_price"] is None or p["previous_price"] == 0:
        return 0
    return (p["current_price"] - p["previous_price"]) / p["previous_price"]


# products-table.tsx sorters — (key, reverse) pairs.
SORTERS = {
    "recent": (lambda r: r["last_change_minutes"], False),
    "price-low": (lambda r: r["current_price"], False),
    "price-high": (lambda r: r["current_price"], True),
    "biggest-drop": (price_delta, False),
    "biggest-increase": (price_delta, True),
    "newest": (lambda r: r["discovered_at"], True),
    "name": (lambda r: r["name"], False),
}


def is_valid_sort(value):
    return bool(value) and value in SORTERS


def sort_products(rows, sort):
    key, reverse = SORTERS.get(sort, SORTERS["recent"])
    return sorted(rows, key=key, reverse=reverse)


def active_filter_count(f, locked=False):
    """products-table.tsx activeFilters (query and sort do not count)."""
    return (
        (1 if f["competitor"] != DEFAULT_FILTERS["competitor"] and not locked else 0)
        + (1 if f["category"] != DEFAULT_FILTERS["category"] else 0)
        + (1 if f["change_type"] != "all" else 0)
        + (1 if f["stock"] != "all" else 0)
        + (1 if f["date_range"] != DEFAULT_FILTERS["date_range"] else 0)
    )


def canonical_query(f, sort, page, competitor_slug_for_name=slugify):
    """writeParams — state → querystring, omitting defaults."""
    params = []
    q = f["query"].strip()
    if q:
        params.append(("q", q))
    if f["competitor"] != DEFAULT_FILTERS["competitor"]:
        params.append(("competitor", competitor_slug_for_name(f["competitor"])))
    if f["category"] != DEFAULT_FILTERS["category"]:
        params.append(("category", category_param(f["category"])))
    if f["change_type"] != "all":
        params.append(("change", f["change_type"]))
    if f["stock"] != "all":
        params.append(("stock", f["stock"]))
    if f["date_range"] != DEFAULT_FILTERS["date_range"]:
        token = RANGE_PARAM_BY_LABEL.get(f["date_range"])
        if token:
            params.append(("range", token))
    if sort != "recent":
        params.append(("sort", sort))
    if page > 1:
        params.append(("page", str(page)))
    return urlencode(params)


def products_csv(rows):
    """productsCsv — headers + rows for the CSV export."""
    headers = [
        "Name",
        "SKU",
        "Competitor",
        "Category",
        "Current price",
        "Previous price",
        "Change",
        "In stock",
        "Last change",
        "Source URL",
    ]
    body = [
        [
            r["name"],
            r["sku"],
            r["competitor"],
            r["category"],
            f"{r['current_price']:.2f}",
            "" if r["previous_price"] is None else f"{r['previous_price']:.2f}",
            r["change"]["label"],
            "Yes" if r["in_stock"] else "No",
            r["last_change"],
            r["source_url"],
        ]
        for r in rows
    ]
    return headers, body
