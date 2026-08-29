import csv
import io
from urllib.parse import urlencode

from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.alerts.data import KIND_TO_TRIGGER
from apps.core.selectors import to_int

from . import filters, selectors, services


def index(request):
    f, sort, page, pattern = selectors.parse_request(request)
    tab = selectors.activity_tab(request)
    context = {
        "kpis": selectors.kpi_cards(request),
        "patterns": selectors.pattern_cards(request),
        "filters": f,
        "select_state": selectors.select_state(request, f, sort),
        "options": selectors.form_options(request),
        "active_filters": filters.count_active_filters(f),
        "saved_views": selectors.saved_view_options(request),
        "page": selectors.events_page(request, f, sort, page),
        "has_events": bool(selectors.all_events(request)),
        "activity_tab": tab,
        "activity_tabs": selectors.ACTIVITY_TABS,
        "charts": {
            "activity": selectors.activity_payload(tab),
            "competitors": selectors.competitor_payload(),
        },
    }
    htmx = getattr(request, "htmx", None)
    if htmx and htmx.target == "change-events":
        return render(request, "changes/partials/events_table.html", context)
    if htmx and htmx.target == "change-activity":
        return render(request, "changes/partials/activity_card.html", context)
    return render(request, "changes/index.html", context)


def export(request):
    """CSV of the currently filtered changes (change-filters.ts changesCsv).

    ?ids=1,2 (bulk-selection export) restricts the filtered set further.
    """
    f, _sort, _page, _pattern = selectors.parse_request(request)
    rows = filters.filter_changes(selectors.all_events(request), f)
    ids_param = request.GET.get("ids", "")
    if ids_param:
        ids = {to_int(v, 0) for v in ids_param.split(",") if v.strip()}
        rows = [r for r in rows if r["id"] in ids]
    data = filters.changes_csv(rows)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(data["headers"])
    writer.writerows(data["rows"])
    response = HttpResponse(buffer.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="rivaltracking-changes.csv"'
    return response


def ask_ai(request):
    """Page-level "Ask AI about changes": forward the current filter context."""
    f, _sort, _page, _pattern = selectors.parse_request(request)
    params = [
        ("prompt", "What changed at my competitors and what should I do about it?")
    ]
    if f["competitor"] != filters.DEFAULT_CHANGE_FILTERS["competitor"]:
        params.append(("competitor", f["competitor"]))
    if f["category"] != filters.DEFAULT_CHANGE_FILTERS["category"]:
        params.append(("category", f["category"]))
    return redirect(reverse("ai:index") + "?" + urlencode(params))


def create_alert(request):
    """"Create alert from filters": map the current filters onto the alerts
    create-dialog deep link (KIND_TO_TRIGGER port from pages/alerts.tsx)."""
    f, _sort, _page, _pattern = selectors.parse_request(request)
    params = [("create", "1")]
    trigger = KIND_TO_TRIGGER.get(f["change_type"])
    if trigger:
        params.append(("trigger", trigger))
    if f["competitor"] != filters.DEFAULT_CHANGE_FILTERS["competitor"]:
        params.append(("competitor", f["competitor"]))
    if f["category"] != filters.DEFAULT_CHANGE_FILTERS["category"]:
        params.append(("category", f["category"]))
    return redirect(reverse("alerts:index") + "?" + urlencode(params))


@require_POST
def watchlist(request):
    """Bulk "Add products to watchlist" from the change events table."""
    ids = [to_int(v, 0) for v in request.POST.get("ids", "").split(",") if v.strip()]
    slugs = []
    for event_id in ids:
        event = selectors.by_id(request, event_id)
        if event and event["product"]["slug"] not in slugs:
            slugs.append(event["product"]["slug"])
    added = services.add_to_watchlist(request, slugs)
    title = (
        f"{added} product{'s' if added > 1 else ''} added to watchlist"
        if added > 0
        else "Already on your watchlist"
    )
    return render(request, "partials/toast.html", {"variant": "success", "title": title})


def drawer(request, event_id):
    """Change detail drawer fragment (HTMX → #drawer-root)."""
    event = selectors.by_id(request, event_id)
    if event is None:
        raise Http404
    return render(request, "changes/partials/detail_drawer.html", {"event": event})
