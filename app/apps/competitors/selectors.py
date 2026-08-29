"""Competitor reads over the ORM (workspace-scoped).

Selectors return the same dict shapes the Phase 1 templates consumed; the
mapping from Competitor rows to those dicts lives in ``row_dict`` so views and
templates are unchanged.
"""
from django.db.models import Sum
from django.utils import timezone

from apps.core.entities import slugify
from apps.core.format import relative_time

from . import filters
from .models import Competitor


def _workspace(request):
    return getattr(request, "workspace", None)


def _queryset(request):
    return Competitor.objects.for_workspace(_workspace(request))


def _minutes_since(dt, now):
    if dt is None:
        return None
    return max(0, int((now - dt).total_seconds() // 60))


def _scan_display(c, now):
    if c.status == Competitor.Status.SCANNING:
        return "Scanning now", 0
    minutes = _minutes_since(c.last_scan_at, now)
    if minutes is None:
        return "Just now", 0
    return relative_time(minutes), minutes


def row_dict(c, now=None):
    """Competitor row → the dict shape competitors-table.tsx expects."""
    now = now or timezone.now()
    label, minutes = _scan_display(c, now)
    return {
        "slug": c.slug,
        "name": c.name,
        "url": c.domain or c.website_url,
        "market": c.market,
        "products": c.products_count,
        "changes_today": c.changes_today,
        "price_drops": c.price_drops,
        "price_increases": c.price_increases,
        "stock_changes": c.stock_changes,
        "last_scan": label,
        "last_scan_minutes": minutes,
        "status": c.status,
        "added_at": c.added_at.isoformat(),
        "note": c.note or None,
    }


def all_rows(request):
    now = timezone.now()
    return [row_dict(c, now) for c in _queryset(request)]


def by_slug(request, slug):
    c = _queryset(request).filter(slug=slug).first()
    return row_dict(c) if c else None


def name_for(request, slug):
    return _queryset(request).filter(slug=slug).values_list("name", flat=True).first()


def slug_for(request, name):
    return _queryset(request).filter(name=name).values_list("slug", flat=True).first()


def header_list(request):
    """[{name, slug}] for the header Run-Scan picker."""
    return list(_queryset(request).values("name", "slug"))


# ---------------------------------------------------------------------------
# Competitors index — view models

KPI_ICONS = {
    "competitors": "boxes",
    "products": "package",
    "changes": "git-compare-arrows",
    "attention": "triangle-alert",
}


def kpi_cards(request):
    qs = _queryset(request)
    agg = qs.aggregate(products=Sum("products_count"), changes=Sum("changes_today"))
    return [
        {"icon": "boxes", "tone": "info", "value": f"{qs.count():,}", "label": "Monitored competitors"},
        {"icon": "package", "tone": "info", "value": f"{agg['products'] or 0:,}", "label": "Products monitored"},
        {"icon": "git-compare-arrows", "tone": "success", "value": f"{agg['changes'] or 0:,}", "label": "Changes today"},
        {"icon": "triangle-alert", "tone": "warning", "value": f"{qs.filter(status=Competitor.Status.ATTENTION).count():,}", "label": "Attention required"},
    ]


# recent-activity.tsx kindMeta + routeFor.
ACTIVITY_META = {
    "prices-down": {"icon": "trending-down", "tone": "bg-success/10 text-success"},
    "new-products": {"icon": "sparkles", "tone": "bg-info/10 text-info"},
    "pages-unavailable": {"icon": "triangle-alert", "tone": "bg-warning/10 text-warning"},
    "out-of-stock": {"icon": "package-x", "tone": "bg-destructive/10 text-destructive"},
    "promotion": {"icon": "badge-percent", "tone": "bg-purple/10 text-purple"},
}


def _activity_route(slug, kind):
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


# Map a ChangeEvent kind → an activity-feed kind (icon/tone bucket).
_CHANGE_TO_ACTIVITY = {
    "drop": "prices-down",
    "increase": "prices-down",
    "new": "new-products",
    "oos": "out-of-stock",
    "removed": "out-of-stock",
    "back": "new-products",
    "promo": "promotion",
    "promo-end": "promotion",
}


def activity_feed(request, limit=6):
    """Recent-activity feed derived from real ChangeEvents (empty when none)."""
    from apps.changes import selectors as change_selectors

    slugs = {name: slug for name, slug in _queryset(request).values_list("name", "slug")}
    feed = []
    for e in change_selectors.all_events(request)[:limit]:
        akind = _CHANGE_TO_ACTIVITY.get(e["kind"], "new-products")
        meta = ACTIVITY_META.get(akind, ACTIVITY_META["prices-down"])
        product = e["product"]["name"]
        feed.append(
            {
                "company": e["competitor"],
                "event": f"{e['label']}{(' · ' + product) if product else ''}",
                "time": e["detected"],
                "kind": akind,
                "icon": meta["icon"],
                "tone": meta["tone"],
                "href": _activity_route(slugs.get(e["competitor"], ""), akind),
            }
        )
    return feed


def monitoring_health(request):
    qs = _queryset(request)
    now = timezone.now()
    healthy = qs.filter(status=Competitor.Status.HEALTHY).count()
    attention = qs.filter(status=Competitor.Status.ATTENTION).count()
    total = qs.count()
    last_scan = qs.exclude(last_scan_at=None).order_by("-last_scan_at").values_list("last_scan_at", flat=True).first()
    next_scan = qs.exclude(next_scan_at=None).order_by("next_scan_at").values_list("next_scan_at", flat=True).first()
    last_label = relative_time(_minutes_since(last_scan, now)) if last_scan else "—"
    if next_scan:
        mins = max(0, int((next_scan - now).total_seconds() // 60))
        next_label = f"in {mins} minutes" if mins < 120 else f"in {mins // 60} hours"
    else:
        next_label = "—"
    healthy_share = (healthy / total) * 100 if total else 0
    stats = [
        {"icon": "check-circle-2", "icon_class": "mt-0.5 size-4 shrink-0 text-success", "value": f"{healthy} competitors", "label": "Healthy"},
        {"icon": "triangle-alert", "icon_class": "mt-0.5 size-4 shrink-0 text-warning", "value": f"{attention} competitor", "label": "Needs attention"},
        {"icon": "clock-3", "icon_class": "mt-0.5 size-4 shrink-0 text-info", "value": last_label, "label": "Last successful scan"},
        {"icon": "calendar-clock", "icon_class": "mt-0.5 size-4 shrink-0 text-purple", "value": next_label, "label": "Next scheduled scan"},
    ]
    return {"stats": stats, "total": total, "healthy": healthy, "healthy_share": healthy_share}


def discovery_suggestions(request, limit=3):
    from apps.discovery import selectors as discovery_selectors

    return [
        {"d": c, "tone_class": discovery_selectors.tone_class(c)}
        for c in discovery_selectors.visible_candidates(request, limit=limit)
    ]


# ---------------------------------------------------------------------------
# Monitored Competitors table fragment

def _num(value):
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
