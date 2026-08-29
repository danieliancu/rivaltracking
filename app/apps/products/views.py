import csv
from urllib.parse import urlencode

from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.alerts.data import KIND_TO_TRIGGER

from apps.ai import insights as ai_insights

from . import filters, selectors, services

FRAGMENT_ID = "products-table"

# product-details.tsx sections.
SECTIONS = [
    ("overview", "Overview"),
    ("price-history", "Price History"),
    ("stock-history", "Stock History"),
    ("changes", "Changes"),
    ("comparison", "Competitor Comparison"),
    ("ai-analysis", "AI Analysis"),
]

TAB_KINDS = {
    "price-history": ["drop", "increase", "promo", "promo-end"],
    "stock-history": ["oos", "back", "missing"],
}

TAB_EMPTY_TEXT = {
    "overview": "Change history begins after the second successful scan.",
    "price-history": "No price changes recorded for this product yet.",
    "stock-history": "No stock changes recorded for this product yet.",
    "changes": "Change history begins after the second successful scan.",
}


def _is_fragment(request):
    return getattr(request, "htmx", None) and request.htmx.target == FRAGMENT_ID


def _fragment_response(request, state):
    context = {**state, "is_fragment": True, "table_url": reverse("products:index")}
    response = render(request, "products/partials/table.html", context)
    push_url = reverse("products:index")
    if state["canonical_qs"]:
        push_url += "?" + state["canonical_qs"]
    response["HX-Push-Url"] = push_url
    return response


def index(request):
    state = selectors.table_state(request, request.GET)
    if _is_fragment(request):
        return _fragment_response(request, state)
    context = {
        **state,
        "table_url": reverse("products:index"),
        "kpis": selectors.kpi_cards(request),
        "price_movement": selectors.price_movement_card(request),
        "categories_chart": selectors.active_categories_chart(request),
        "filter_options": selectors.filter_options(request),
        "ai_summary": ai_insights.activity_summary(request.workspace),
        "ask_ai_href": reverse("ai:index")
        + "?"
        + urlencode({"prompt": "What new products have appeared recently?"}),
    }
    return render(request, "products/index.html", context)


def detail(request, slug):
    row = selectors.by_slug(request, slug)
    if row is None:
        return render(request, "products/detail.html", {"row": None})

    events = selectors.events_for(request, slug)
    tab = request.GET.get("tab")
    if tab not in dict(SECTIONS):
        tab = "overview"
    shown_events = (
        selectors.events_by_kinds(events, TAB_KINDS[tab]) if tab in TAB_KINDS else events
    )

    alert_params = {"create": "1"}
    trigger = KIND_TO_TRIGGER.get(row["change"]["kind"])
    if trigger:
        alert_params["trigger"] = trigger
    alert_params.update(
        {"competitor": row["competitor"], "category": row["category"], "product": row["name"]}
    )

    context = {
        "row": row,
        "events": events,
        "shown_events": shown_events,
        "events_empty_text": TAB_EMPTY_TEXT.get(tab, TAB_EMPTY_TEXT["overview"]),
        "tab": tab,
        "sections": [
            {
                "id": section_id,
                "label": label,
                "href": request.path if section_id == "overview" else f"{request.path}?tab={section_id}",
            }
            for section_id, label in SECTIONS
        ],
        "compare": selectors.compare_context(row),
        "create_alert_url": reverse("alerts:index") + "?" + urlencode(alert_params),
        "ask_ai_url": reverse("ai:index") + f"?product={row['slug']}",
        "changes_url": reverse("changes:index") + f"?product={row['slug']}",
        "ai_title": f"AI Analysis — {row['name']}",
        "price_movement": selectors.price_movement_card(request) if tab == "price-history" else None,
    }
    return render(request, "products/detail.html", context)


def compare_drawer(request, slug):
    """Compare-competitors drawer fragment (HTMX → #drawer-root)."""
    row = selectors.by_slug(request, slug)
    compare = selectors.compare_context(row) if row else None
    if compare is None:
        raise Http404
    return render(
        request, "products/partials/compare_drawer.html", {"row": row, "compare": compare}
    )


def compare_selected(request):
    """Bulk 'Compare' — drawer for the first matched selected product, else a toast."""
    slugs = request.GET.getlist("selected")
    if len(slugs) < 2:
        return render(
            request,
            "partials/toast.html",
            {"variant": "info", "title": "Select at least two products to compare."},
        )
    match = next(
        (r for r in selectors.all_rows(request) if r["slug"] in slugs and r.get("matched")), None
    )
    if match is None:
        return render(
            request,
            "partials/toast.html",
            {
                "variant": "info",
                "title": "No matched listings",
                "description": "The selected products have no matched competitor listings yet.",
            },
        )
    return render(
        request,
        "products/partials/compare_drawer.html",
        {"row": match, "compare": selectors.compare_context(match)},
    )


def export_csv(request):
    """Future: GET /api/products/export — same querystring contract as the table."""
    state = selectors.table_state(request, request.GET)
    rows = filters.sort_products(
        filters.filter_products(selectors.all_rows(request), state["filters"]), state["sort"]
    )
    selected = request.GET.getlist("selected")
    if selected:
        picked = [r for r in rows if r["slug"] in selected]
        rows = picked or rows
    headers, body = filters.products_csv(rows)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="rivaltracking-products.csv"'
    writer = csv.writer(response)
    writer.writerow(headers)
    writer.writerows(body)
    return response


@require_POST
def watchlist_toggle(request, slug):
    """Star toggle — swaps the star button and toasts."""
    row = selectors.by_slug(request, slug)
    if row is None:
        raise Http404
    added = services.toggle_watchlist(request, slug)
    return render(
        request,
        "products/partials/star_button.html",
        {
            "row": row,
            "starred": added,
            "toast_title": "Added to watchlist" if added else "Removed from watchlist",
        },
    )


@require_POST
def watchlist_add(request):
    """Bulk 'Add to watchlist' — re-renders the fragment with selection kept."""
    slugs = request.POST.getlist("selected")
    added = services.add_to_watchlist(request, slugs)
    if added > 0:
        toast_title = f"{added} product{'s' if added > 1 else ''} added to watchlist"
    else:
        toast_title = "Already on your watchlist"
    state = selectors.table_state(
        request,
        request.POST,
        locked_competitor=request.POST.get("locked") or None,
        preselected=slugs,
    )
    context = {
        **state,
        "is_fragment": True,
        "table_url": reverse("products:index"),
        "toast_title": toast_title,
    }
    return render(request, "products/partials/table.html", context)
