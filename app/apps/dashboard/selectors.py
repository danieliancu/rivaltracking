"""Overview dataset reads and chart payload assembly."""
from django.urls import reverse

from apps.core.mock.store import MockStore

from .data import OVERVIEW_BY_RANGE

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


def dataset(range_key):
    return OVERVIEW_BY_RANGE.get(range_key, OVERVIEW_BY_RANGE["30d"])


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
    return [
        {**s, "token": STOCK_COLORS[s["name"]]} for s in data["stock"]
    ]


def selected_competitor(request):
    """The Overview competitor context (session slug, else first row)."""
    rows = MockStore(request).get("competitors")
    if not rows:
        return None
    slug = request.session.get("selected_competitor")
    return next((c for c in rows if c["slug"] == slug), rows[0])
