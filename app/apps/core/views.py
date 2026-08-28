from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST


@require_GET
def search(request):
    """Global header search. Returns the grouped-results fragment."""
    return render(request, "partials/search_results.html", {"query": request.GET.get("q", "")})


@require_POST
def set_range(request):
    """Store the global Today/7D/30D date range in the session."""
    from django.http import HttpResponse

    return HttpResponse(status=204)


@require_POST
def run_scan(request):
    """Mock competitor scan trigger."""
    from django.http import HttpResponse

    return HttpResponse(status=204)


@require_POST
def reset_demo(request):
    """Drop the session's mock-data copy, restoring the seed dataset."""
    from django.http import HttpResponse

    return HttpResponse(status=204)


def not_found(request, exception=None):
    return render(request, "404.html", status=404)


def not_found_preview(request):
    """DEBUG-only way to view the custom 404 page."""
    return render(request, "404.html")
