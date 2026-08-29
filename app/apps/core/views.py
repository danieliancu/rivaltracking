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
    """Header 'Run Scan' — enqueues real ScanJob(s) on the scraping queue."""
    from apps.competitors.models import Competitor
    from apps.scanning.models import ScanJob
    from apps.scanning.services import enqueue_scan

    name = request.POST.get("competitor", "All competitors")
    qs = Competitor.objects.for_workspace(getattr(request, "workspace", None))
    if name != "All competitors":
        qs = qs.filter(name=name)

    jobs = [enqueue_scan(c, trigger=ScanJob.Trigger.MANUAL) for c in qs]
    for job in jobs:
        job.refresh_from_db()

    completed = [j for j in jobs if j.status == ScanJob.Status.COMPLETED]
    if jobs and len(completed) == len(jobs):
        changes = sum(j.changes_detected for j in completed)
        toast = {
            "variant": "success",
            "title": "Scan complete",
            "description": f"{changes} new changes detected across {name}.",
        }
    else:
        toast = {
            "variant": "info",
            "title": "Scan started",
            "description": f"Scanning {name}…",
        }
    return render(request, "partials/toast.html", {**toast})


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
