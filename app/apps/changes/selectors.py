"""Change-event reads over the mock store, plus Changes-page view models."""
from urllib.parse import urlencode

from apps.alerts.data import KIND_TO_TRIGGER
from apps.competitors import selectors as competitor_selectors
from apps.core.entities import category_param, slugify
from apps.core.mock.store import MockStore
from apps.core.selectors import paginate, to_int

from . import filters
from .data import (
    CHANGE_ACTIVITY,
    CHANGE_FILTER_OPTIONS,
    CHANGE_KPIS,
    CHANGE_PATTERNS,
    CHANGE_SORT_OPTIONS,
    COMPETITOR_ACTIVITY,
    SAVED_VIEWS,
)


def all_events(request):
    return MockStore(request).get("change_events")


def by_id(request, event_id):
    for event in all_events(request):
        if event["id"] == event_id:
            return event
    return None


def recent_for_competitor(request, competitor_name, kinds=None, limit=5):
    """dashboard/changes-table.tsx: latest events for one competitor."""
    rows = [
        e
        for e in all_events(request)
        if e["competitor"] == competitor_name and (not kinds or e["kind"] in kinds)
    ]
    return rows[:limit]


# ---------------------------------------------------------------------------
# Changes page — pages/changes.tsx

# changes.tsx kpiIcons: data icon key → lucide glyph.
KPI_ICONS = {
    "activity": "activity",
    "down": "trending-down",
    "up": "trending-up",
    "stock": "package-x",
    "new": "sparkles",
    "promo": "badge-percent",
}


def kpi_cards():
    return [dict(k, icon=KPI_ICONS.get(k["icon"], "activity")) for k in CHANGE_KPIS]


def _slug_for(request, name):
    return competitor_selectors.slug_for(request, name) or slugify(name)


def parse_request(request):
    """URL params → (filters, sort, page, pattern) — the table's URL sync."""
    params = request.GET
    f = filters.change_filters_from_params(
        params, lambda slug: competitor_selectors.name_for(request, slug)
    )
    sort_param = params.get("sort")
    sort = sort_param if filters.is_valid_change_sort(sort_param) else "recent"
    page = max(1, to_int(params.get("page"), 1))
    pattern = next(
        (p for p in CHANGE_PATTERNS if p["id"] == params.get("pattern")), None
    )
    if pattern:
        f = filters.pattern_filters(pattern)
    return f, sort, page, pattern


def events_page(request, f, sort, page):
    """Filtered + sorted + paginated rows, annotated with the alert trigger id."""
    rows = filters.sort_changes(filters.filter_changes(all_events(request), f), sort)
    page_data = paginate(rows, page)
    page_data["rows"] = [
        dict(e, trigger=KIND_TO_TRIGGER.get(e["kind"], "")) for e in page_data["rows"]
    ]
    page_data["ids"] = [e["id"] for e in page_data["rows"]]
    return page_data


def select_state(request, f, sort):
    """Current filters as the form's URL-token values (defaults are '')."""
    default = filters.DEFAULT_CHANGE_FILTERS
    return {
        "q": f["query"],
        "competitor": ""
        if f["competitor"] == default["competitor"]
        else _slug_for(request, f["competitor"]),
        "type": "" if f["change_type"] == "all" else f["change_type"],
        "category": ""
        if f["category"] == default["category"]
        else category_param(f["category"]),
        "impact": "" if f["importance"] == "all" else f["importance"],
        "range": ""
        if f["date_range"] == default["date_range"]
        else filters.CHANGE_RANGE_PARAM_BY_LABEL.get(f["date_range"], ""),
        "product": f["product_slug"] or "",
        "sort": "" if sort == "recent" else sort,
    }


def form_options(request):
    """Select options with URL-token values (CHANGE_FILTER_OPTIONS port)."""
    opts = CHANGE_FILTER_OPTIONS
    return {
        "competitors": [{"value": "", "label": opts["competitors"][0]}]
        + [
            {"value": _slug_for(request, name), "label": name}
            for name in opts["competitors"][1:]
        ],
        "change_types": [{"value": "", "label": "All changes"}]
        + opts["change_type_groups"],
        "categories": [{"value": "", "label": opts["categories"][0]}]
        + [
            {"value": category_param(name), "label": name}
            for name in opts["categories"][1:]
        ],
        "importance": [
            {"value": "" if o["value"] == "all" else o["value"], "label": o["label"]}
            for o in opts["importance"]
        ],
        "date_ranges": [
            {
                "value": ""
                if label == "Today"
                else filters.CHANGE_RANGE_PARAM_BY_LABEL.get(label, ""),
                "label": label,
            }
            for label in opts["date_ranges"]
        ],
        "sorts": [
            {"value": "" if o["value"] == "recent" else o["value"], "label": o["label"]}
            for o in CHANGE_SORT_OPTIONS
        ],
    }


def saved_view_options(request):
    """SAVED_VIEWS with the three-param patch each view applies (applyView)."""
    out = []
    for v in SAVED_VIEWS:
        stored = v["filters"]
        competitor = stored.get("competitor")
        patch = urlencode(
            [
                ("competitor", _slug_for(request, competitor) if competitor else ""),
                ("type", stored.get("kind") or ""),
                ("impact", stored.get("importance") or ""),
            ]
        )
        out.append({"id": v["id"], "label": v["label"], "patch": patch})
    return out


def pattern_cards(request):
    """CHANGE_PATTERNS with the CTA deep link (?pattern=… + mapped filters)."""
    cards = []
    for p in CHANGE_PATTERNS:
        stored = p["filters"]
        params = []
        if stored.get("competitor"):
            params.append(("competitor", _slug_for(request, stored["competitor"])))
        if stored.get("kind"):
            params.append(("type", stored["kind"]))
        if stored.get("category"):
            params.append(("category", category_param(stored["category"])))
        params.append(("range", "30d"))
        params.append(("pattern", p["id"]))
        cards.append(dict(p, href="?" + urlencode(params)))
    return cards


# ---------------------------------------------------------------------------
# Charts — changes/change-activity.tsx, changes/active-competitors.tsx

ACTIVITY_SERIES = [
    ("price", "Price", "chart-1"),
    ("stock", "Stock", "warning"),
    ("product", "Products", "chart-2"),
    ("promotions", "Promotions", "purple"),
]

ACTIVITY_TABS = [("all", "All")] + [(key, label) for key, label, _ in ACTIVITY_SERIES]


def activity_tab(request):
    key = request.GET.get("activity", "all")
    return key if key in {k for k, _ in ACTIVITY_TABS} else "all"


def activity_payload(tab):
    return {
        "type": "line",
        "labels": [row["time"] for row in CHANGE_ACTIVITY],
        "series": [
            {
                "label": label,
                "data": [row[key] for row in CHANGE_ACTIVITY],
                "color": color,
            }
            for key, label, color in ACTIVITY_SERIES
            if tab == "all" or key == tab
        ],
        "options": {},
    }


def competitor_payload():
    return {
        "type": "hbar",
        "labels": [c["name"] for c in COMPETITOR_ACTIVITY],
        "series": [
            {"data": [c["changes"] for c in COMPETITOR_ACTIVITY], "color": "chart-1"}
        ],
        "options": {"labels": True, "barSize": 18, "labelWidth": 132},
    }
