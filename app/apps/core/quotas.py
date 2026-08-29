"""Workspace usage + guardrails (scaffold; no billing/Stripe in this phase).

Tracks the numbers a future plan would enforce so limits can be applied later
without redesign. Enforcement is intentionally not wired to billing yet.
"""
from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

DEFAULT_LIMITS = {
    "competitors": 25,
    "active_listings": 25000,
    "scans_per_day": 200,
    "ai_analyses_per_day": 500,
}


def usage(workspace):
    from apps.ai.models import ChangeAnalysis
    from apps.catalogue.models import Product, ProductListing
    from apps.competitors.models import Competitor
    from apps.scanning.models import ScanJob

    day_ago = timezone.now() - timedelta(days=1)
    return {
        "competitors": Competitor.objects.for_workspace(workspace).count(),
        "products": Product.objects.for_workspace(workspace).count(),
        "active_listings": ProductListing.objects.for_workspace(workspace).filter(active=True).count(),
        "scans_last_24h": ScanJob.objects.for_workspace(workspace).filter(queued_at__gte=day_ago).count(),
        "ai_analyses_last_24h": ChangeAnalysis.objects.for_workspace(workspace).filter(created_at__gte=day_ago).count(),
    }


def within_limits(workspace, resource, limits=None):
    """Whether a workspace is under the given resource limit (scaffold)."""
    limits = limits or DEFAULT_LIMITS
    cap = limits.get(resource)
    if cap is None:
        return True
    return usage(workspace).get(resource, 0) < cap
