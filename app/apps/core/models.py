"""Core models.

WorkspaceDemoState is the Phase 2 bridge for the four placeholder apps
(Alerts, Reports, Ask AI, Discovery): their user-mutable demo state lives here
as workspace-scoped JSON instead of in the per-browser session. Phase 3
replaces it with real AlertRule/Report/Conversation models + engines.
"""
from django.db import models


class WorkspaceDemoState(models.Model):
    workspace = models.OneToOneField(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="demo_state"
    )
    data = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Demo state for {self.workspace}"
