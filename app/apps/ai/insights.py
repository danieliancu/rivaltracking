"""Deterministic AI-insight one-liners for the dashboard/insight cards.

Real, workspace-scoped summaries computed from ChangeEvents. Returns "" when
there is not enough data, so the card shows an honest empty state instead of
fabricated market commentary.
"""
from __future__ import annotations

from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from apps.changes.models import ChangeEvent


def activity_summary(workspace, *, days=7):
    T = ChangeEvent.Type
    since = timezone.now() - timedelta(days=days)
    ev = ChangeEvent.objects.for_workspace(workspace).filter(detected_at__gte=since)
    total = ev.count()
    if not total:
        return ""
    parts = [f"{total} changes detected across your competitors in the last {days} days."]
    top = ev.values("competitor__name").annotate(n=Count("id")).order_by("-n").first()
    if top and top["competitor__name"]:
        parts.append(f"{top['competitor__name']} was the most active ({top['n']}).")
    drops = ev.filter(event_type=T.PRICE_DECREASE).count()
    stockouts = ev.filter(event_type=T.STOCK_OUT).count()
    if drops:
        parts.append(f"{drops} price reductions detected.")
    if stockouts:
        parts.append(f"{stockouts} products went out of stock at competitors.")
    return " ".join(parts)
