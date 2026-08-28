"""Competitor reads over the mock store."""
from apps.core.entities import slugify
from apps.core.mock.store import MockStore

from . import filters
from .data import ACTIVITY_EVENTS, COMPETITOR_KPIS, MONITORING_HEALTH


def all_rows(request):
    return MockStore(request).get("competitors")


def by_slug(request, slug):
    for row in all_rows(request):
        if row["slug"] == slug:
            return row
    return None


def name_for(request, slug):
    row = by_slug(request, slug)
    return row["name"] if row else None


def slug_for(request, name):
    for row in all_rows(request):
        if row["name"] == name:
            return row["slug"]
    return None


# ---------------------------------------------------------------------------
# Competitors index — pages/competitors.tsx view models

# competitors.tsx kpiIcons — id → lucide glyph.
KPI_ICONS = {
    "competitors": "boxes",
    "products": "package",
    "changes": "git-compare-arrows",
    "attention": "triangle-alert",
}


def kpi_cards():
    return [
        {"icon": KPI_ICONS.get(k["id"], "boxes"), "tone": k["tone"], "value": k["value"], "label": k["label"]}
        for k in COMPETITOR_KPIS
    ]


# recent-activity.tsx kindMeta + routeFor.
ACTIVITY_META = {
    "prices-down": {"icon": "trending-down", "tone": "bg-success/10 text-success"},
    "new-products": {"icon": "sparkles", "tone": "bg-info/10 text-info"},
    "pages-unavailable": {"icon": "triangle-alert", "tone": "bg-warning/10 text-warning"},
    "out-of-stock": {"icon": "package-x", "tone": "bg-destructive/10 text-destructive"},
    "promotion": {"icon": "badge-percent", "tone": "bg-purple/10 text-purple"},
}


def _activity_route(request, event):
    slug = slug_for(request, event["company"]) or slugify(event["company"])
    kind = event["kind"]
    if kind == "prices-down":
        return f"/changes/?type=price-decrease&competitor={slug}"
    if kind == "new-products":
        return f"/products/?change=new&competitor={slug}"
    if kind == "pages-unavailable":
        return f"/competitors/{slug}/"
    if kind == "out-of-stock":
        return f"/changes/?type=out-of-stock&competitor={slug}"
    if kind == "promotion":
        return f"/changes/?type=promotion-started&competitor={slug}"
    return "/changes/"


def activity_feed(request):
    """ACTIVITY_EVENTS decorated with icon/tone + the per-kind deep link."""
    feed = []
    for e in ACTIVITY_EVENTS:
        meta = ACTIVITY_META.get(e["kind"], ACTIVITY_META["prices-down"])
        feed.append({**e, "icon": meta["icon"], "tone": meta["tone"], "href": _activity_route(request, e)})
    return feed


# monitoring-health.tsx stats + two-segment bar.
def monitoring_health():
    h = MONITORING_HEALTH
    total = h["healthy"] + h["attention"]
    healthy_share = (h["healthy"] / total) * 100 if total else 0
    stats = [
        {"icon": "check-circle-2", "icon_class": "mt-0.5 size-4 shrink-0 text-success", "value": f"{h['healthy']} competitors", "label": "Healthy"},
        {"icon": "triangle-alert", "icon_class": "mt-0.5 size-4 shrink-0 text-warning", "value": f"{h['attention']} competitor", "label": "Needs attention"},
        {"icon": "clock-3", "icon_class": "mt-0.5 size-4 shrink-0 text-info", "value": h["last_successful_scan"], "label": "Last successful scan"},
        {"icon": "calendar-clock", "icon_class": "mt-0.5 size-4 shrink-0 text-purple", "value": h["next_scheduled_scan"], "label": "Next scheduled scan"},
    ]
    return {"stats": stats, "total": total, "healthy": h["healthy"], "healthy_share": healthy_share}


# "Competitors you may be missing" — 3 non-dismissed discovery candidates.
def discovery_suggestions(request, limit=3):
    from apps.discovery import selectors as discovery_selectors

    return [
        {"d": c, "tone_class": discovery_selectors.tone_class(c)}
        for c in discovery_selectors.visible_candidates(request, limit=limit)
    ]


# ---------------------------------------------------------------------------
# Monitored Competitors table fragment — competitors-table.tsx

def _num(value):
    """competitors-table.tsx num(): thousands-separated or an em dash."""
    return "—" if value is None else f"{value:,}"


def table_state(request, params):
    rows = all_rows(request)
    f = filters.filters_from_params(params)
    visible = filters.sort_rows(filters.filter_rows(rows, f), f["sort"])
    view = [
        {**r, "products_display": _num(r["products"]), "stock_display": _num(r["stock_changes"])}
        for r in visible
    ]
    return {
        "filters": f,
        "rows": view,
        "has_rows": bool(rows),
        "canonical_qs": filters.canonical_query(f),
        "status_tabs": filters.STATUS_FILTERS,
        "sort_options": [{"value": k, "label": v} for k, v in filters.SORT_LABELS.items()],
    }
