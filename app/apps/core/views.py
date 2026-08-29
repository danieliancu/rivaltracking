from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from apps.core.search import global_search
from apps.core.store import WorkspaceStore


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
    """Header 'Run Scan'. Deterministic placeholder — scanning is Phase 3."""
    from django.utils import timezone

    from apps.competitors.models import Competitor

    name = request.POST.get("competitor", "All competitors")
    changes = 6 if name == "All competitors" else 3
    qs = Competitor.objects.for_workspace(getattr(request, "workspace", None))
    if name != "All competitors":
        qs = qs.filter(name=name)
    qs.update(last_scan_at=timezone.now())
    return render(
        request,
        "partials/toast.html",
        {
            "variant": "success",
            "title": "Scan complete",
            "description": f"{changes} new changes detected across {name}.",
        },
    )


@require_POST
def sign_out(request):
    """Legacy sign-out endpoint — now a real logout (header posts to accounts:logout)."""
    from django.contrib.auth import logout
    from django.shortcuts import redirect

    logout(request)
    return redirect("accounts:login")


@require_POST
def reset_demo(request):
    """Restore the seed dataset for the current workspace (ORM + demo state)."""
    from apps.core.seed import seed_workspace

    if getattr(request, "workspace", None) is not None:
        seed_workspace(request.workspace)
        WorkspaceStore(request).reset()
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
