"""Competitors index + competitor details — pages/competitors.tsx and
pages/competitor-details.tsx."""
import re
from urllib.parse import urlencode, urlparse

from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.changes import selectors as change_selectors
from apps.core.entities import slugify
from apps.products import selectors as product_selectors

from apps.ai import insights as ai_insights

from . import selectors, services
from .data import SCAN_STAGES

FRAGMENT_ID = "competitors-table"

# competitor-details.tsx sections. "overview" clears the ?tab param.
SECTIONS = [
    ("overview", "Overview"),
    ("products", "Products"),
    ("price-history", "Price History"),
    ("stock", "Stock"),
    ("promotions", "Promotions"),
    ("ai-analysis", "AI Analysis"),
]

# ChangesTable kinds + copy per detail tab.
TAB_CHANGES = {
    "price-history": {
        "kinds": ["drop", "increase"],
        "title": "Price Change Events",
        "description": "Detected price movements at {name}",
    },
    "stock": {
        "kinds": ["oos", "back", "missing"],
        "title": "Stock Activity",
        "description": "Stock-outs and restocks detected at {name}",
    },
    "promotions": {
        "kinds": ["promo", "promo-end"],
        "title": "Promotion Activity",
        "description": "Promotions detected at {name}",
    },
    "ai-analysis": {
        "kinds": None,
        "title": "Evidence — Recent Changes",
        "description": "Verified events behind the analysis for {name}",
    },
    "overview": {"kinds": None, "title": None, "description": None},
}


# ---------------------------------------------------------------------------
# Index

def _is_fragment(request):
    return getattr(request, "htmx", None) and request.htmx.target == FRAGMENT_ID


def _fragment_response(request, params, toasts=None):
    state = selectors.table_state(request, params)
    context = {**state, "table_url": reverse("competitors:index"), "toasts": toasts or []}
    response = render(request, "competitors/partials/table.html", context)
    push_url = reverse("competitors:index")
    if state["canonical_qs"]:
        push_url += "?" + state["canonical_qs"]
    response["HX-Push-Url"] = push_url
    return response


def index(request):
    if _is_fragment(request):
        return _fragment_response(request, request.GET)
    state = selectors.table_state(request, request.GET)
    context = {
        **state,
        "table_url": reverse("competitors:index"),
        "toasts": [],
        "kpis": selectors.kpi_cards(request),
        "activity": selectors.activity_feed(request),
        "health": selectors.monitoring_health(request),
        "ai_summary": ai_insights.activity_summary(request.workspace),
        "suggestions": selectors.discovery_suggestions(request),
        "ask_ai_href": reverse("ai:index")
        + "?"
        + urlencode({"prompt": "Analyse portfolio activity across my competitors"}),
    }
    return render(request, "competitors/index.html", context)


# ---------------------------------------------------------------------------
# Add-competitor dialog

def add_dialog(request):
    """Add-competitor dialog fragment (HTMX → #modal-root), form phase."""
    return render(request, "competitors/partials/add_dialog.html")


def _validate_url(raw):
    """Port of add-competitor-dialog.tsx validateUrl()."""
    value = raw.strip()
    if not value:
        return None, "Enter the competitor's website address."
    candidate = value if re.match(r"^https?://", value, re.I) else f"https://{value}"
    try:
        host = urlparse(candidate).hostname or ""
    except ValueError:
        host = ""
    if not host or "." not in host:
        return None, "Enter a valid website address, e.g. competitor.com."
    return re.sub(r"^www\.", "", host), None


@require_POST
def add(request):
    """Validate + add the competitor, then return the scanning phase."""
    raw = request.POST.get("url", "")
    host, error = _validate_url(raw)
    if error is None and any(
        c["slug"] == slugify(host) for c in selectors.all_rows(request)
    ):
        error = "You are already monitoring this competitor."
    if error:
        return render(
            request,
            "competitors/partials/add_form.html",
            {"error": error, "url_value": raw},
        )
    row = services.add_competitor(request, host)
    return render(
        request,
        "competitors/partials/add_scanning.html",
        {
            "stages": SCAN_STAGES,
            "added_name": row["name"],
            "added_slug": row["slug"],
            "added_products": f"{row['products'] or 0:,}",
        },
    )


# ---------------------------------------------------------------------------
# Row mutations — each returns the refreshed table fragment + toast(s)

@require_POST
def run_scan(request, slug):
    row = selectors.by_slug(request, slug)
    if row is None:
        raise Http404
    name = row["name"]
    result = services.run_scan(request, slug)
    if result and result["status"] == "completed":
        toasts = [
            {
                "variant": "success",
                "title": "Scan complete",
                "description": f"{result['new_changes']} new changes detected across {name}.",
            }
        ]
    else:
        toasts = [
            {"variant": "info", "title": "Scan started", "description": f"Scanning {name}…"}
        ]
    return _fragment_response(request, request.POST, toasts)


@require_POST
def pause_resume(request, slug):
    row = selectors.by_slug(request, slug)
    if row is None:
        raise Http404
    name = row["name"]
    if row["status"] == "paused":
        services.set_status(request, slug, "healthy")
        toast = {"variant": "success", "title": "Monitoring resumed", "description": name}
    else:
        services.set_status(request, slug, "paused")
        toast = {"variant": "info", "title": "Monitoring paused", "description": name}
    return _fragment_response(request, request.POST, [toast])


@require_POST
def remove(request, slug):
    row = selectors.by_slug(request, slug)
    name = row["name"] if row else slug
    services.remove_competitor(request, slug)
    toast = {
        "variant": "info",
        "title": "Competitor removed",
        "description": (
            f"{name} is no longer monitored. Historical data removal is a separate "
            "action in Settings."
        ),
    }
    return _fragment_response(request, request.POST, [toast])


# ---------------------------------------------------------------------------
# Monitoring-settings drawer

# monitoring-settings-drawer.tsx frequencies + trackingRows.
FREQUENCIES = ["Every 24 hours", "Every 12 hours", "Every 6 hours"]
TRACKING_ROWS = [
    ("track_prices", "Track prices", "Detect price increases and decreases."),
    ("track_stock", "Track stock", "Detect stock-outs and restocks."),
    ("track_products", "Track new/removed products", "Detect catalogue changes."),
    ("track_promotions", "Track promotions", "Detect promotions starting and ending."),
]


def monitoring_drawer(request, slug):
    """Monitoring-settings drawer fragment (HTMX → #drawer-root)."""
    row = selectors.by_slug(request, slug)
    if row is None:
        raise Http404
    config = services.get_monitoring_config(request, slug)
    return render(
        request,
        "competitors/partials/monitoring_drawer.html",
        {
            "row": row,
            "config": config,
            "frequencies": FREQUENCIES,
            "tracking_rows": [
                {"name": key, "label": label, "hint": hint, "checked": config.get(key)}
                for key, label, hint in TRACKING_ROWS
            ],
        },
    )


def remove_dialog(request, slug):
    """Remove-competitor confirm dialog (HTMX → #modal-root)."""
    row = selectors.by_slug(request, slug)
    if row is None:
        raise Http404
    return render(request, "competitors/partials/remove_dialog.html", {"row": row})


@require_POST
def save_monitoring(request, slug):
    row = selectors.by_slug(request, slug)
    if row is None:
        raise Http404
    config = {
        "frequency": request.POST.get("frequency", services.DEFAULT_CONFIG["frequency"]),
        "track_prices": request.POST.get("track_prices") == "on",
        "track_stock": request.POST.get("track_stock") == "on",
        "track_products": request.POST.get("track_products") == "on",
        "track_promotions": request.POST.get("track_promotions") == "on",
    }
    services.save_monitoring_config(request, slug, config)
    return render(
        request,
        "partials/toast.html",
        {
            "variant": "success",
            "title": "Settings saved",
            "description": f"Monitoring settings updated for {row['name']}.",
        },
    )


# ---------------------------------------------------------------------------
# Competitor details

def _overview_stats(row):
    products = f"{row['products']:,}" if row["products"] is not None else "—"
    changes = str(row["changes_today"]) if row["changes_today"] is not None else "—"
    if row["price_drops"] is None:
        price = "—"
    else:
        price = f"{row['price_drops']} ↓ / {row['price_increases']} ↑"
    return [
        {"label": "Products monitored", "value": products},
        {"label": "Changes today", "value": changes},
        {"label": "Price changes", "value": price},
        {"label": "Last scan", "value": row["last_scan"]},
    ]


def detail(request, slug):
    row = selectors.by_slug(request, slug)
    if row is None:
        return render(request, "competitors/detail.html", {"row": None})

    tab = request.GET.get("tab")
    if tab not in dict(SECTIONS):
        tab = "overview"
    name = row["name"]
    competitor = {"name": name, "slug": slug}
    context = {
        "row": row,
        "tab": tab,
        "competitor": competitor,
        "sections": [
            {
                "id": sid,
                "label": label,
                "href": request.path if sid == "overview" else f"{request.path}?tab={sid}",
            }
            for sid, label in SECTIONS
        ],
        "changes_url": reverse("changes:index") + f"?competitor={slug}",
        "ai_title": f"AI Analysis — {name}",
        "ask_ai_url": reverse("ai:index") + f"?competitor={slug}",
    }

    if tab == "overview":
        context["overview_stats"] = _overview_stats(row)

    if tab == "products":
        state = product_selectors.table_state(request, request.GET, locked_competitor=slug)
        context.update(state)
        context["filter_options"] = product_selectors.filter_options(request)
        context["products_fragment_url"] = reverse(
            "competitors:products_fragment", args=[slug]
        )
        context["table_url"] = f"{request.path}?tab=products"

    if tab in TAB_CHANGES:
        cfg = TAB_CHANGES[tab]
        context["recent_events"] = change_selectors.recent_for_competitor(
            request, name, kinds=cfg["kinds"]
        )
        context["table_title"] = cfg["title"]
        context["table_description"] = (
            cfg["description"].format(name=name) if cfg["description"] else None
        )

    return render(request, "competitors/detail.html", context)


def products_fragment(request, slug):
    """Embedded products table fragment for the competitor Products tab
    (locked to this competitor, no URL sync)."""
    row = selectors.by_slug(request, slug)
    if row is None:
        raise Http404
    state = product_selectors.table_state(request, request.GET, locked_competitor=slug)
    context = {
        **state,
        "is_fragment": True,
        "table_url": reverse("competitors:detail", args=[slug]) + "?tab=products",
    }
    return render(request, "products/partials/table.html", context)
