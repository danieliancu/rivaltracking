from django.shortcuts import render
from django.views.decorators.http import require_POST

from apps.changes import selectors as change_selectors
from apps.core.mock.store import MockStore
from apps.discovery import selectors as discovery_selectors

from . import selectors


def _context(request):
    range_key = request.session.get("date_range", "30d")
    data = selectors.dataset(range_key)
    competitor = selectors.selected_competitor(request)
    competitor_name = competitor["name"] if competitor else "your competitors"
    return {
        "kpis": selectors.kpi_cards(data),
        "charts": selectors.chart_payloads(data),
        "stock_legend": selectors.stock_legend(data),
        "range_label": selectors.RANGE_LABELS[range_key],
        "range_labels": selectors.RANGE_LABELS,
        "competitor": competitor,
        "competitors": MockStore(request).get("competitors"),
        "recent_events": change_selectors.recent_for_competitor(request, competitor_name),
        "suggestions": [
            {"d": d, "tone_class": discovery_selectors.tone_class(d)}
            for d in discovery_selectors.visible_candidates(request, limit=4)
        ],
    }


def overview(request):
    context = _context(request)
    if getattr(request, "htmx", None) and request.htmx.target == "overview-metrics":
        return render(request, "dashboard/partials/metrics.html", context)
    if getattr(request, "htmx", None) and request.htmx.target == "overview-changes":
        return render(request, "dashboard/partials/changes_card.html", context)
    return render(request, "dashboard/overview.html", context)


@require_POST
def select_competitor(request):
    """Overview competitor picker: updates the session and re-renders the
    recent-changes card plus (out-of-band) the picker pill."""
    request.session["selected_competitor"] = request.POST.get("slug") or None
    context = _context(request)
    return render(request, "dashboard/partials/select_competitor_response.html", context)
