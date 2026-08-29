from urllib.parse import quote

from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_POST

from . import selectors, services
from .data import DISCOVERY_MODES, DISCOVERY_STAGES


def _cluster_qs(cluster):
    return f"?cluster={quote(cluster)}" if cluster else ""


def _page_context(request):
    cluster = request.GET.get("cluster") or None
    return {
        "cluster": cluster,
        "cluster_qs": _cluster_qs(cluster),
        "clusters": selectors.cluster_cards(request, cluster),
        "candidates": selectors.visible_candidates(request, cluster),
    }


def index(request):
    context = _page_context(request)
    if request.htmx and request.htmx.target == "discovery-results":
        return render(request, "discovery/partials/results_card.html", context)
    if request.htmx and request.htmx.target == "discovery-clusters":
        return render(request, "discovery/partials/cluster_cards.html", context)
    return render(request, "discovery/index.html", context)


def dialog(request):
    """Discovery dialog fragment (HTMX → #modal-root), form phase."""
    return render(
        request,
        "discovery/partials/discovery_dialog.html",
        {"modes": DISCOVERY_MODES},
    )


@require_POST
def run(request):
    """Run discovery, then return the staged running fragment + result toast."""
    found = services.run_discovery(request)
    if found > 0:
        description = f"{found} suggestion{'' if found == 1 else 's'} refreshed."
    else:
        description = "No new candidates found — existing suggestions are up to date."
    return render(
        request,
        "discovery/partials/discovery_run.html",
        {
            "stages": DISCOVERY_STAGES,
            "toast": {
                "variant": "success",
                "title": "Discovery complete",
                "description": description,
            },
        },
    )


@require_POST
def monitor(request, slug):
    """Start monitoring a discovery candidate; returns the updated row
    (swapped in place) plus a toast. `variant=page` returns the richer
    Discovery-page row instead of the dashboard card row."""
    candidate = services.monitor_candidate(request, slug)
    if candidate is None:
        raise Http404
    context = {
        "d": selectors.by_slug(request, slug),
        "toast": {
            "variant": "success",
            "title": "Competitor added",
            "description": f"Now monitoring {candidate['name']} — initial snapshot queued.",
        },
    }
    if request.POST.get("variant") == "page":
        context["cluster_qs"] = _cluster_qs(request.GET.get("cluster") or None)
        return render(request, "discovery/partials/monitor_page_response.html", context)
    return render(request, "discovery/partials/monitor_response.html", context)


def why_match(request, slug):
    """Why-match drawer fragment (HTMX → #drawer-root)."""
    d = selectors.by_slug(request, slug)
    if d is None:
        raise Http404
    return render(
        request,
        "discovery/partials/why_match_drawer.html",
        {
            "d": d,
            "products_display": f"{d['catalogue_profile']['products']:,}",
            "cluster_qs": _cluster_qs(request.GET.get("cluster") or None),
        },
    )


def compare(request, slug):
    """Compare-catalogue drawer fragment (HTMX → #drawer-root)."""
    d = selectors.by_slug(request, slug)
    if d is None:
        raise Http404
    return render(
        request,
        "discovery/partials/compare_drawer.html",
        {
            "d": d,
            "products_display": f"{d['catalogue_profile']['products']:,}",
            "reference": selectors.reference_profile(request),
        },
    )


@require_POST
def not_relevant(request, slug):
    """Mark a candidate not relevant; re-renders the results card + counts."""
    d = selectors.by_slug(request, slug)
    if d is None:
        raise Http404
    services.mark_not_relevant(request, slug)
    context = _page_context(request)
    context["toast"] = {
        "variant": "info",
        "title": "Feedback saved",
        "description": f"{d['name']} will no longer be suggested.",
    }
    return render(request, "discovery/partials/results_refresh.html", context)


@require_POST
def dismiss(request, slug):
    """Dismiss a suggestion; re-renders the results card + counts."""
    d = selectors.by_slug(request, slug)
    if d is None:
        raise Http404
    services.dismiss_candidate(request, slug)
    context = _page_context(request)
    context["toast"] = {"variant": "info", "title": "Suggestion dismissed"}
    return render(request, "discovery/partials/results_refresh.html", context)
