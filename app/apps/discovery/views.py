from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_POST

from . import selectors, services


def index(request):
    return render(request, "stub.html", {"page_title": "Discovery"})


@require_POST
def monitor(request, slug):
    """Start monitoring a discovery candidate; returns the updated row
    (swapped in place) plus a toast."""
    candidate = services.monitor_candidate(request, slug)
    if candidate is None:
        raise Http404
    return render(
        request,
        "discovery/partials/monitor_response.html",
        {
            "d": selectors.by_slug(request, slug),
            "toast": {
                "variant": "success",
                "title": "Competitor added",
                "description": f"Now monitoring {candidate['name']} — initial snapshot queued.",
            },
        },
    )
