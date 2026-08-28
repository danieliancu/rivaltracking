from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from apps.core.mock.store import MockStore
from apps.core.search import global_search


@require_GET
def search(request):
    """Header search — returns the grouped-results fragment."""
    query = request.GET.get("q", "")
    results = global_search(request, query)
    return render(
        request,
        "partials/search_results.html",
        {"results": results, "query": query.strip()},
    )


@require_POST
def set_range(request):
    """Store the global Today/7D/30D range and re-render the tabs."""
    value = request.POST.get("range", "30d")
    if value not in {"today", "7d", "30d"}:
        value = "30d"
    request.session["date_range"] = value
    response = render(request, "partials/range_tabs.html", {"date_range": value})
    response["HX-Trigger"] = "range:changed"
    return response


@require_POST
def run_scan(request):
    """Mock competitor scan. Future: POST /api/competitors/:id/scan"""
    name = request.POST.get("competitor", "All competitors")
    store = MockStore(request)
    # Deterministic mock outcome, mirroring scanToastMessage in format.ts.
    changes = 6 if name == "All competitors" else 3
    store.mutate("competitors", lambda rows: _mark_scanned(rows, name))
    return render(
        request,
        "partials/toast.html",
        {
            "variant": "success",
            "title": "Scan complete",
            "description": f"{changes} new changes detected across {name}.",
        },
    )


def _mark_scanned(rows, name):
    for row in rows:
        if name in ("All competitors", row["name"]):
            row["last_scan"] = "Just now"
            row["last_scan_minutes"] = 0


@require_POST
def sign_out(request):
    """Authentication arrives in a later phase — honest placeholder."""
    return render(
        request,
        "partials/toast.html",
        {
            "variant": "info",
            "title": "Authentication is not connected yet",
            "description": "Sign-in and sign-out arrive with the Django backend.",
        },
    )


@require_POST
def reset_demo(request):
    """Drop the session's mock-data copy, restoring the seed dataset."""
    MockStore(request).reset()
    request.session.pop("date_range", None)
    request.session.pop("selected_competitor", None)
    response = HttpResponse(status=204)
    response["HX-Refresh"] = "true"
    return response


def not_found(request, exception=None):
    return render(request, "404.html", status=404)


def not_found_preview(request):
    """DEBUG-only way to view the custom 404 page."""
    return render(request, "404.html")
