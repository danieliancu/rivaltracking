"""Pure change filtering/sorting/CSV ported from prototype lib/change-filters.ts
(plus the kind/range param-token maps it imports from lib/product-filters.ts and
the sort comparators from changes/change-events-table.tsx).

The backend will eventually do this server-side (GET /api/changes?...).
"""
from apps.core.entities import category_from_param

from .data import CHANGE_FILTER_OPTIONS, CHANGE_SORT_OPTIONS

DEFAULT_CHANGE_FILTERS = {
    "query": "",
    "competitor": CHANGE_FILTER_OPTIONS["competitors"][0],
    "change_type": "all",
    "category": CHANGE_FILTER_OPTIONS["categories"][0],
    "importance": "all",
    "date_range": "Today",
    "product_slug": None,
}

RANGE_MINUTES_BY_LABEL = {
    "Today": 24 * 60,
    "24 hours": 24 * 60,
    "7 days": 7 * 24 * 60,
    "30 days": 30 * 24 * 60,
}

# "Custom" has no URL token in the prototype (it never round-trips through the
# URL there either); we add one so the option survives a server render cycle.
CHANGE_RANGE_LABEL_BY_PARAM = {
    "today": "Today",
    "24h": "24 hours",
    "7d": "7 days",
    "30d": "30 days",
    "custom": "Custom",
}

CHANGE_RANGE_PARAM_BY_LABEL = {
    "Today": "today",
    "24 hours": "24h",
    "7 days": "7d",
    "30 days": "30d",
    "Custom": "custom",
}

# product-filters.ts kindByParam: spec-level tokens ("price-decrease") → kind.
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

# product-filters.ts rangeLabelByParam (secondary fallback in the prototype).
RANGE_LABEL_BY_PARAM = {"today": "Today", "7d": "7 days", "30d": "30 days"}


def kind_from_param(param):
    if not param:
        return "all"
    return KIND_BY_PARAM.get(param.lower(), "all")


def range_label_from_param(param):
    return RANGE_LABEL_BY_PARAM.get(param.lower()) if param else None


def change_filters_from_params(params, name_for_slug):
    """change-filters.ts changeFiltersFromParams over request.GET.

    `name_for_slug` maps a competitor slug to its display name (or None).
    """
    competitor_slug = params.get("competitor")
    category = params.get("category")
    range_param = params.get("range")
    impact = params.get("impact") or ""
    competitor = name_for_slug(competitor_slug) if competitor_slug else None
    return {
        "query": params.get("q") or "",
        "competitor": competitor or DEFAULT_CHANGE_FILTERS["competitor"],
        "change_type": kind_from_param(params.get("type")),
        "category": (
            (category_from_param(category, CHANGE_FILTER_OPTIONS["categories"]) if category else None)
            or DEFAULT_CHANGE_FILTERS["category"]
        ),
        "importance": impact if impact in ("high", "medium", "low") else "all",
        "date_range": (
            (CHANGE_RANGE_LABEL_BY_PARAM.get(range_param.lower()) if range_param else None)
            or range_label_from_param(range_param)
            or DEFAULT_CHANGE_FILTERS["date_range"]
        ),
        "product_slug": params.get("product") or None,
    }


def pattern_filters(pattern):
    """change-events-table.tsx onApplyPattern: defaults + the pattern's filters."""
    filters = dict(DEFAULT_CHANGE_FILTERS)
    filters["date_range"] = "30 days"
    stored = pattern["filters"]
    if stored.get("competitor"):
        filters["competitor"] = stored["competitor"]
    filters["change_type"] = stored.get("kind") or "all"
    if stored.get("category"):
        filters["category"] = stored["category"]
    return filters


def filter_changes(rows, f):
    """change-filters.ts filterChanges."""
    q = f["query"].strip().lower()
    max_minutes = RANGE_MINUTES_BY_LABEL.get(f["date_range"])
    out = []
    for r in rows:
        if q and not (
            q in r["product"]["name"].lower()
            or q in r["competitor"].lower()
            or q in r["category"].lower()
        ):
            continue
        if f["competitor"] != DEFAULT_CHANGE_FILTERS["competitor"] and r["competitor"] != f["competitor"]:
            continue
        if f["change_type"] != "all" and r["kind"] != f["change_type"]:
            continue
        if f["category"] != DEFAULT_CHANGE_FILTERS["category"] and r["category"] != f["category"]:
            continue
        if f["importance"] != "all" and r["impact"] != f["importance"]:
            continue
        if f["product_slug"] and r["product"]["slug"] != f["product_slug"]:
            continue
        if max_minutes is not None and r["detected_minutes"] > max_minutes:
            continue
        out.append(r)
    return out


def count_active_filters(f):
    """change-events-table.tsx activeFilters (the search query is not counted)."""
    return sum(
        [
            f["competitor"] != DEFAULT_CHANGE_FILTERS["competitor"],
            f["change_type"] != "all",
            f["category"] != DEFAULT_CHANGE_FILTERS["category"],
            f["importance"] != "all",
            f["date_range"] != DEFAULT_CHANGE_FILTERS["date_range"],
            bool(f["product_slug"]),
        ]
    )


# ---------------------------------------------------------------------------
# Sorting — change-events-table.tsx sorters

IMPACT_RANK = {"high": 0, "medium": 1, "low": 2}

VALID_SORTS = {o["value"] for o in CHANGE_SORT_OPTIONS}


def _pct(event):
    secondary = event.get("secondary")
    return float(secondary.replace("%", "")) if secondary else 0.0


SORT_KEYS = {
    "recent": (lambda e: e["detected_minutes"], False),
    "impact": (lambda e: IMPACT_RANK[e["impact"]], False),
    "biggest-drop": (_pct, False),
    "biggest-increase": (_pct, True),
    "competitor": (lambda e: e["competitor"], False),
    "product": (lambda e: e["product"]["name"], False),
}


def is_valid_change_sort(value):
    return bool(value) and value in VALID_SORTS


def sort_changes(rows, sort):
    key, reverse = SORT_KEYS.get(sort, SORT_KEYS["recent"])
    return sorted(rows, key=key, reverse=reverse)


# ---------------------------------------------------------------------------
# CSV export — change-filters.ts changesCsv

def changes_csv(rows):
    return {
        "headers": [
            "Change",
            "Product",
            "SKU",
            "Competitor",
            "Category",
            "Previous",
            "Current",
            "Impact",
            "Detected",
        ],
        "rows": [
            [
                r["label"],
                r["product"]["name"],
                r["product"]["sku"],
                r["competitor"],
                r["category"],
                r["previous"],
                r["current"],
                r["impact"],
                r["detected_at"],
            ]
            for r in rows
        ],
    }
