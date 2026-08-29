"""Change-event reads over the ORM, plus Changes-page view models.

``event_dict`` rebuilds the exact Phase 1 change-event dict from a ChangeEvent
row (competitor/product joined, display strings from metadata) so the events
table, detail drawer and the product/competitor detail tabs are unchanged. The
pure filter/sort helpers in filters.py then run over those dicts.
"""
from urllib.parse import urlencode

from django.utils import timezone

from apps.alerts.data import KIND_TO_TRIGGER
from apps.competitors import selectors as competitor_selectors
from apps.core.entities import category_param, slugify
from apps.core.format import relative_time
from apps.core.selectors import PAGE_SIZE, paginate, to_int

from . import filters
from .data import (
    CHANGE_FILTER_OPTIONS,
    CHANGE_KPIS,
    CHANGE_SORT_OPTIONS,
    SAVED_VIEWS,
)
from .models import ChangeEvent


def _workspace(request):
    return getattr(request, "workspace", None)


def _minutes_since(dt, now):
    if dt is None:
        return None
    return max(0, int((now - dt).total_seconds() // 60))


def event_dict(event, now=None):
    """ChangeEvent row → the Phase 1 change-event dict."""
    now = now or timezone.now()
    product = event.product
    meta = event.metadata or {}
    analysis = getattr(event, "analysis", None)
    minutes = _minutes_since(event.detected_at, now)
    source_url = meta.get("source_url") or (event.listing.source_url if event.listing else "")
    return {
        "id": event.id,
        "type": event.event_type.upper(),
        "kind": event.kind,
        "label": event.label,
        "product": {
            "slug": product.slug if product else "",
            "name": product.name if product else "",
            "sku": product.sku if product else "",
            "tone": product.tone if product else "",
            "icon": product.icon if product else "package",
        },
        "competitor": event.competitor.name,
        "category": product.category if product else "",
        "previous": event.previous_value,
        "current": event.new_value,
        "secondary": event.secondary or None,
        "secondary_tone": event.secondary_tone or None,
        "impact": event.impact,
        "detected": relative_time(minutes),
        "detected_minutes": minutes if minutes is not None else 0,
        "source_url": source_url,
        "detected_at": meta.get("detected_at", ""),
        "first_seen_at": meta.get("first_seen_at", ""),
        "last_confirmed_at": meta.get("last_confirmed_at", ""),
        "last_scanned": meta.get("last_scanned", ""),
        "difference": event.difference or None,
        "evidence": meta.get("evidence", {}),
        "ai_note": (
            (analysis.why_it_matters or analysis.summary) if analysis else meta.get("ai_note", "")
        ),
    }


def _events_qs(request):
    return (
        ChangeEvent.objects.for_workspace(_workspace(request))
        .select_related("competitor", "product", "listing", "analysis")
    )


def all_events(request):
    now = timezone.now()
    return [event_dict(e, now) for e in _events_qs(request)]


def by_id(request, event_id):
    event = _events_qs(request).filter(id=event_id).first()
    return event_dict(event) if event else None


def recent_for_competitor(request, competitor_name, kinds=None, limit=5):
    """dashboard/changes-table.tsx: latest events for one competitor."""
    now = timezone.now()
    qs = _events_qs(request).filter(competitor__name=competitor_name)
    if kinds:
        qs = qs.filter(kind__in=list(kinds))
    return [event_dict(e, now) for e in qs[:limit]]


# ---------------------------------------------------------------------------
# Changes page — pages/changes.tsx

KPI_ICONS = {
    "activity": "activity",
    "down": "trending-down",
    "up": "trending-up",
    "stock": "package-x",
    "new": "sparkles",
    "promo": "badge-percent",
}


def kpi_cards(request):
    qs = _events_qs(request)
    T = ChangeEvent.Type
    values = {
        "today": qs.filter(detected_at__date=timezone.localdate()).count(),
        "decreases": qs.filter(event_type=T.PRICE_DECREASE).count(),
        "increases": qs.filter(event_type=T.PRICE_INCREASE).count(),
        "stock": qs.filter(event_type__in=[T.STOCK_IN, T.STOCK_OUT]).count(),
        "new": qs.filter(event_type=T.PRODUCT_NEW).count(),
        "promos": qs.filter(event_type__in=[T.PROMOTION_STARTED, T.PROMOTION_ENDED]).count(),
    }
    return [
        dict(k, icon=KPI_ICONS.get(k["icon"], "activity"), value=f"{values.get(k['id'], 0):,}")
        for k in CHANGE_KPIS
    ]


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
    return f, sort, page, None


def _apply_db_filters(qs, f):
    """Translate the change filter dict into ORM Q filters (DB-level)."""
    from django.db.models import Q
    from django.utils import timezone

    q = f["query"].strip()
    if q:
        qs = qs.filter(
            Q(product__name__icontains=q)
            | Q(competitor__name__icontains=q)
            | Q(product__category__icontains=q)
        )
    if f["competitor"] != filters.DEFAULT_CHANGE_FILTERS["competitor"]:
        qs = qs.filter(competitor__name=f["competitor"])
    if f["change_type"] != "all":
        qs = qs.filter(kind=f["change_type"])
    if f["category"] != filters.DEFAULT_CHANGE_FILTERS["category"]:
        qs = qs.filter(product__category=f["category"])
    if f["importance"] != "all":
        qs = qs.filter(impact=f["importance"])
    if f["product_slug"]:
        qs = qs.filter(product__slug=f["product_slug"])
    max_minutes = filters.RANGE_MINUTES_BY_LABEL.get(f["date_range"])
    if max_minutes is not None:
        since = timezone.now() - timezone.timedelta(minutes=max_minutes)
        qs = qs.filter(detected_at__gte=since)
    return qs


def _db_order(sort):
    from django.db.models import Case, IntegerField, Value, When

    if sort == "impact":
        rank = Case(
            When(impact="high", then=Value(0)),
            When(impact="medium", then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        )
        return ["_impact_rank", "-detected_at"], rank
    if sort == "competitor":
        return ["competitor__name", "-detected_at"], None
    if sort == "product":
        return ["product__name", "-detected_at"], None
    return ["-detected_at"], None  # recent (default)


def events_page(request, f, sort, page):
    """DB-level filter → sort → paginate; presents only the current page.

    The two percentage-based sorts need the parsed %, which isn't a DB column,
    so they sort the (already DB-filtered) page set in Python.
    """
    now = timezone.now()
    qs = _apply_db_filters(_events_qs(request), f)

    if sort in ("biggest-drop", "biggest-increase"):
        rows = filters.sort_changes([event_dict(e, now) for e in qs], sort)
        page_data = paginate(rows, page)
    else:
        order, annotation = _db_order(sort)
        if annotation is not None:
            qs = qs.annotate(_impact_rank=annotation)
        qs = qs.order_by(*order)
        total = qs.count()
        page_count = max(1, -(-total // PAGE_SIZE))
        page = max(1, min(page, page_count))
        start = (page - 1) * PAGE_SIZE
        window = list(qs[start : start + PAGE_SIZE])
        rows = [event_dict(e, now) for e in window]
        page_data = {
            "rows": rows,
            "page": page,
            "page_count": page_count,
            "from": start + 1 if total else 0,
            "to": start + len(rows),
            "total": total,
        }
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
    competitors = [{"value": "", "label": opts["competitors"][0]}] + [
        {"value": c["slug"], "label": c["name"]}
        for c in competitor_selectors.header_list(request)
    ]
    return {
        "competitors": competitors,
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


_PATTERN_META = {
    "drop": ("trending-down", "text-success"),
    "increase": ("trending-up", "text-destructive"),
    "oos": ("package-x", "text-warning"),
    "back": ("package-check", "text-success"),
    "new": ("sparkles", "text-info"),
    "removed": ("trash-2", "text-destructive"),
    "promo": ("badge-percent", "text-purple"),
}
_KIND_LABEL = {
    "drop": "price drops", "increase": "price rises", "oos": "stock-outs",
    "back": "restocks", "new": "new products", "removed": "removals",
    "promo": "promotions",
}


def pattern_cards(request, limit=3):
    """Derived 'major change patterns' — real (competitor, kind) clusters."""
    from datetime import timedelta

    from django.db.models import Count

    since = timezone.now() - timedelta(days=7)
    rows = (
        _events_qs(request)
        .filter(detected_at__gte=since)
        .values("competitor__name", "competitor__slug", "kind")
        .annotate(n=Count("id"))
        .order_by("-n")[: limit * 2]
    )
    cards = []
    for r in rows:
        if r["n"] < 2:
            continue
        kind, comp, slug = r["kind"], r["competitor__name"], r["competitor__slug"]
        icon, tone = _PATTERN_META.get(kind, ("activity", "text-info"))
        label = _KIND_LABEL.get(kind, "changes")
        params = urlencode([("competitor", slug or ""), ("type", kind), ("range", "7d")])
        cards.append(
            {
                "id": f"{slug}-{kind}",
                "title": f"{r['n']} {label} at {comp}",
                "competitor": comp,
                "stat": str(r["n"]),
                "stat_detail": "in the last 7 days",
                "meta": "",
                "cta": "View changes",
                "icon": icon,
                "tone": tone,
                "href": "?" + params,
            }
        )
        if len(cards) >= limit:
            break
    return cards


# ---------------------------------------------------------------------------
# Charts — presentational analytics (headline series kept from the seed).

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


# activity series key → the ChangeEvent types it aggregates.
_ACTIVITY_TYPES = {
    "price": [ChangeEvent.Type.PRICE_DECREASE, ChangeEvent.Type.PRICE_INCREASE],
    "stock": [ChangeEvent.Type.STOCK_IN, ChangeEvent.Type.STOCK_OUT],
    "product": [ChangeEvent.Type.PRODUCT_NEW, ChangeEvent.Type.PRODUCT_REMOVED],
    "promotions": [ChangeEvent.Type.PROMOTION_STARTED, ChangeEvent.Type.PROMOTION_ENDED],
}


def activity_payload(request, tab):
    """Change-activity line chart derived from real ChangeEvents (last 7 days)."""
    from datetime import timedelta

    from django.db.models import Count
    from django.db.models.functions import TruncDate

    since = timezone.now() - timedelta(days=7)
    events = _events_qs(request).filter(detected_at__gte=since)
    by_day_type = {}
    for row in (
        events.annotate(d=TruncDate("detected_at"))
        .values("d", "event_type")
        .annotate(n=Count("id"))
    ):
        by_day_type.setdefault(row["d"], {})[row["event_type"]] = row["n"]
    days = sorted(by_day_type)
    labels = [f"{d:%b} {d.day}" for d in days]

    def _series(key):
        types = _ACTIVITY_TYPES[key]
        return [sum(by_day_type.get(d, {}).get(t, 0) for t in types) for d in days]

    return {
        "type": "line",
        "labels": labels,
        "series": [
            {"label": label, "data": _series(key), "color": color}
            for key, label, color in ACTIVITY_SERIES
            if tab == "all" or key == tab
        ],
        "options": {},
    }


def competitor_payload(request):
    """Most-active competitors (real ChangeEvent counts)."""
    from django.db.models import Count

    rows = (
        _events_qs(request)
        .values("competitor__name")
        .annotate(n=Count("id"))
        .order_by("-n")[:8]
    )
    return {
        "type": "hbar",
        "labels": [r["competitor__name"] for r in rows],
        "series": [{"data": [r["n"] for r in rows], "color": "chart-1"}],
        "options": {"labels": True, "barSize": 18, "labelWidth": 132},
    }
