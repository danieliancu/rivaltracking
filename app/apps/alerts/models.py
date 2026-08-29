"""Alert rules + fired alerts (real models replacing the placeholder store)."""
from django.db import models

from apps.core.scoping import WorkspaceManager


class AlertRule(models.Model):
    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="alert_rules"
    )
    name = models.CharField(max_length=200)
    type_group = models.CharField(max_length=20)  # price/stock/products/promotions/patterns
    condition = models.CharField(max_length=200)
    competitors = models.CharField(max_length=200, default="All competitors")
    category = models.CharField(max_length=120, blank=True)
    frequency = models.CharField(max_length=40, default="Immediate")
    priority = models.CharField(max_length=10, default="medium")
    enabled = models.BooleanField(default=True)
    pattern_based = models.BooleanField(default=False)
    # Raw dialog fields (trigger_id/operator/threshold/pattern_*/brand/product)
    # + delivery channels; keeps the create/edit dialog exact.
    config = models.JSONField(default=dict, blank=True)
    channels = models.JSONField(default=list, blank=True)  # ["in_app", "email"]
    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["workspace", "enabled"])]

    def __str__(self):
        return self.name


class Alert(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        VIEWED = "viewed", "Viewed"

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="alerts"
    )
    rule = models.ForeignKey(
        AlertRule, on_delete=models.SET_NULL, null=True, blank=True, related_name="alerts"
    )
    change_event = models.ForeignKey(
        "changes.ChangeEvent", on_delete=models.CASCADE, null=True, blank=True,
        related_name="alerts",
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)
    title = models.CharField(max_length=200, blank=True)
    message = models.CharField(max_length=400, blank=True)
    triggered_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    delivery = models.JSONField(default=dict, blank=True)
    # Presentational payload for the recent-alerts UI (kept exact).
    payload = models.JSONField(default=dict, blank=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-triggered_at"]
        indexes = [
            models.Index(fields=["workspace", "-triggered_at"]),
            models.Index(fields=["workspace", "status"]),
        ]

    def __str__(self):
        return self.title or f"Alert {self.pk}"
