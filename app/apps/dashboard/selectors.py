"""Overview dataset reads and chart payload assembly (ORM-derived).

`build_dataset(request, range_key)` produces the same dataset dict the Phase 1
static seeds did — {kpis, price_trend, categories, stock, total_products} —
computed from the workspace's ORM data over the selected Today/7D/30D window,
so kpi_cards/chart_payloads/stock_legend and the templates are unchanged.
"""
import statistics
from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone

from apps.catalogue.models import PriceSnapshot, ProductListing, StockStatus
from apps.changes.models import ChangeEvent
from apps.competitors import selectors as competitor_selectors
from apps.competitors.models import Competitor
from apps.core.selectors import RANGE_MINUTES

# kpi-cards.tsx: id → icon and deep link.
KPI_ICONS = {
    "monitored": "package",
    "new": "sparkles",
    "reductions": "trending-down",
    "increases": "trending-up",
    "oos": "package-x",
    "promos": "percent",
}

KPI_ROUTES = {
    "monitored": "/products",
    "new": "/products?change=new",
    "reductions": "/changes?type=price-decrease",
    "increases": "/changes?type=price-increase",
    "oos": "/products?stock=out",
    "promos": "/changes?type=promotion-started",
}

RANGE_LABELS = {"today": "Today", "7d": "Last 7 days", "30d": "Last 30 days"}

STOCK_COLORS = {
    "In Stock": "success",
    "Out of Stock": "warning",
    "Back in Stock": "chart-1",
}


def _workspace(request):
    return getattr(request, "workspace", None)


def _window_start(range_key, now):
    return now - timedelta(minutes=RANGE_MINUTES.get(range_key, RANGE_MINUTES["30d"]))


def _kpis(ws, events, now):
    T = ChangeEvent.Type
    monitored = Competitor.objects.for_workspace(ws).aggregate(n=Sum("products_count"))["n"] or 0
    by_type = {
        row["event_type"]: row["n"]
        for row in events.values("event_type").annotate(n=Count("id"))
    }
    return [
        ["monitored", "Products monitored", f"{monitored:,}", "info"],
        ["new", "New products", f"{by_type.get(T.PRODUCT_NEW, 0):,}", "success"],
        ["reductions", "Price reductions", f"{by_type.get(T.PRICE_DECREASE, 0):,}", "success"],
        ["increases", "Price increases", f"{by_type.get(T.PRICE_INCREASE, 0):,}", "danger"],
        ["oos", "Out of stock", f"{by_type.get(T.STOCK_OUT, 0):,}", "warning"],
        ["promos", "New promotions", f"{by_type.get(T.PROMOTION_STARTED, 0):,}", "purple"],
    ]


def _categories(events):
    rows = (
        events.exclude(product__isnull=True)
        .values("product__category")
        .annotate(n=Count("id"))
        .order_by("-n")[:5]
    )
    total = sum(r["n"] for r in rows) or 1
    return [
        {"name": r["product__category"] or "Uncategorised", "value": round(r["n"] / total * 100)}
        for r in rows
    ]


def _stock(ws, events):
    listings = ProductListing.objects.for_workspace(ws).filter(active=True)
    total = listings.count()
    out = listings.filter(current_stock_status=StockStatus.OUT_OF_STOCK).count()
    back = (
        events.filter(event_type=ChangeEvent.Type.STOCK_IN)
        .values("listing").distinct().count()
    )
    in_stock = max(total - out - back, 0)
    rows = [
        ("In Stock", in_stock),
        ("Out of Stock", out),
        ("Back in Stock", back),
    ]
    return [
        {
            "name": name,
            "value": value,
            "percent": f"{(value / total * 100) if total else 0:.1f}%",
        }
        for name, value in rows
    ], total


def _price_trend(ws, window_start):
    snaps = (
        PriceSnapshot.objects.for_workspace(ws)
        .filter(captured_at__gte=window_start)
        .order_by("captured_at")
        .values_list("captured_at", "price")
    )
    by_date = {}
    for captured_at, price in snaps:
        by_date.setdefault(captured_at.date(), []).append(float(price))
    dates = sorted(by_date)
    if not dates:
        return []
    base_avg = statistics.fmean(by_date[dates[0]])
    base_med = statistics.median(by_date[dates[0]])
    trend = []
    for d in dates:
        prices = by_date[d]
        avg = statistics.fmean(prices)
        med = statistics.median(prices)
        trend.append(
            {
                "date": f"{d:%b} {d.day}",
                "median": round((med / base_med - 1) * 100, 1) if base_med else 0.0,
                "average": round((avg / base_avg - 1) * 100, 1) if base_avg else 0.0,
            }
        )
    return trend


def build_dataset(request, range_key):
    ws = _workspace(request)
    now = timezone.now()
    events = ChangeEvent.objects.for_workspace(ws).filter(
        detected_at__gte=_window_start(range_key, now)
    )
    stock, total = _stock(ws, events)
    return {
        "kpis": _kpis(ws, events, now),
        "price_trend": _price_trend(ws, _window_start(range_key, now)),
        "categories": _categories(events),
        "stock": stock,
        "total_products": f"{total:,}",
    }


def kpi_cards(data):
    cards = []
    for kpi_id, label, value, tone in data["kpis"]:
        cards.append(
            {
                "icon": KPI_ICONS.get(kpi_id, "package"),
                "tone": tone,
                "value": value,
                "label": label,
                "href": KPI_ROUTES.get(kpi_id),
            }
        )
    return cards


def chart_payloads(data):
    trend = data["price_trend"]
    categories = data["categories"]
    stock = data["stock"]
    return {
        "trend": {
            "type": "line",
            "labels": [p["date"] for p in trend],
            "series": [
                {"label": "Median Price", "data": [p["median"] for p in trend], "color": "chart-1"},
                {"label": "Average Price", "data": [p["average"] for p in trend], "color": "chart-2", "dashed": True},
            ],
            "options": {"yMin": -10, "yMax": 10, "yTicks": [-10, -5, 0, 5, 10], "yStep": 5, "percent": True},
        },
        "categories": {
            "type": "hbar",
            "labels": [c["name"] for c in categories],
            "series": [{"data": [c["value"] for c in categories], "color": "chart-1"}],
            "options": {"labels": True, "percent": True, "xMax": 100, "barSize": 18, "labelWidth": 112},
        },
        "stock": {
            "type": "donut",
            "labels": [s["name"] for s in stock],
            "series": [{"data": [s["value"] for s in stock], "colors": [STOCK_COLORS[s["name"]] for s in stock]}],
            "options": {"centerTotal": data["total_products"], "centerLabel": "Total"},
        },
    }


def stock_legend(data):
    return [{**s, "token": STOCK_COLORS[s["name"]]} for s in data["stock"]]


def selected_competitor(request):
    """The Overview competitor context (session slug, else first row)."""
    rows = competitor_selectors.all_rows(request)
    if not rows:
        return None
    slug = request.session.get("selected_competitor")
    return next((c for c in rows if c["slug"] == slug), rows[0])
