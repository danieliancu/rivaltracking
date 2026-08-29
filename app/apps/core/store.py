"""Workspace-scoped copy-on-write store for the placeholder apps.

Same façade the Phase 1 mock store had (get / mutate / replace / reset) so
Alerts / Reports / Ask AI / Discovery selectors and services needed only to
swap ``MockStore`` for ``WorkspaceStore``. Reads fall through to the immutable
``apps/<app>/data.py`` seeds until a collection is first mutated, at which
point that collection is copied into the workspace's WorkspaceDemoState row
(DB-backed, tenant-isolated, survives sessions).

This is a deliberate Phase 2 bridge: Phase 3 replaces these collections with
real models + engines.
"""
from copy import deepcopy

from .models import WorkspaceDemoState


def _seeds():
    """The placeholder collections still served from static seed data."""
    from apps.ai import data as ai
    from apps.alerts import data as alerts
    from apps.discovery import data as discovery
    from apps.reports import data as reports

    return {
        "alert_rules": alerts.ALERT_RULES,
        "recent_alerts": alerts.RECENT_ALERTS,
        "reports": reports.GENERATED_REPORTS,
        "report_schedules": reports.REPORT_SCHEDULES,
        "conversations": ai.CONVERSATION_HISTORY,
        "discovery_candidates": discovery.DISCOVERY_CANDIDATES_SEED,
    }


class WorkspaceStore:
    def __init__(self, request):
        self.request = request
        self.workspace = getattr(request, "workspace", None)

    def _row(self):
        if self.workspace is None:
            return None
        row, _ = WorkspaceDemoState.objects.get_or_create(
            workspace=self.workspace, defaults={"data": {}}
        )
        return row

    def get(self, name):
        """Read a collection. Treat the result as immutable."""
        row = self._row()
        if row is not None and name in row.data:
            return row.data[name]
        return _seeds()[name]

    def mutate(self, name, fn):
        """Apply fn to the workspace's own copy of a collection and persist."""
        row = self._row()
        if row is None:
            return None
        if name not in row.data:
            row.data[name] = deepcopy(_seeds()[name])
        result = fn(row.data[name])
        row.save(update_fields=["data", "updated_at"])
        return result

    def replace(self, name, value):
        """Replace a collection wholesale (e.g. filtered deletions)."""
        row = self._row()
        if row is None:
            return
        row.data[name] = value
        row.save(update_fields=["data", "updated_at"])

    def reset(self):
        """Drop the workspace's demo-state copy, restoring the seed data."""
        if self.workspace is not None:
            WorkspaceDemoState.objects.filter(workspace=self.workspace).delete()
