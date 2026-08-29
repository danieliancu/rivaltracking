"""Tenant-scoping helpers shared by every app's selectors and services.

The golden rule: never query a business model without a workspace filter.
`scoped_get_or_404` returns 404 (never 403 with detail) for ids/slugs that
belong to another workspace, so existence is not leaked across tenants.
"""
from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404


def scoped_get_or_404(model_or_qs, workspace, **kwargs):
    """Fetch one object constrained to ``workspace`` or raise Http404.

    Accepts a model class or a queryset. A missing/None workspace (e.g. a user
    with no membership) always raises 404 rather than leaking global rows.
    """
    if workspace is None:
        raise Http404("No active workspace.")
    return get_object_or_404(model_or_qs, workspace=workspace, **kwargs)


class WorkspaceQuerySet(models.QuerySet):
    def for_workspace(self, workspace):
        if workspace is None:
            return self.none()
        return self.filter(workspace=workspace)


class WorkspaceManager(models.Manager.from_queryset(WorkspaceQuerySet)):
    """Default manager exposing ``.for_workspace(workspace)``."""
