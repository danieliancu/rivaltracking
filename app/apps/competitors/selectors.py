"""Competitor reads over the mock store."""
from apps.core.mock.store import MockStore


def all_rows(request):
    return MockStore(request).get("competitors")


def by_slug(request, slug):
    for row in all_rows(request):
        if row["slug"] == slug:
            return row
    return None


def name_for(request, slug):
    row = by_slug(request, slug)
    return row["name"] if row else None


def slug_for(request, name):
    for row in all_rows(request):
        if row["name"] == name:
            return row["slug"]
    return None
