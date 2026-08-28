from django.http import Http404
from django.shortcuts import render

from . import selectors


def index(request):
    return render(request, "stub.html", {"page_title": "Changes"})


def drawer(request, event_id):
    """Change detail drawer fragment (HTMX → #drawer-root)."""
    event = selectors.by_id(request, event_id)
    if event is None:
        raise Http404
    return render(request, "changes/partials/detail_drawer.html", {"event": event})
