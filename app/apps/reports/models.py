"""Report + ReportSchedule models (real, replacing the placeholder store)."""
from django.db import models

from apps.core.scoping import WorkspaceManager


class Report(models.Model):
    class Status(models.TextChoices):
        GENERATING = "generating", "Generating"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="reports"
    )
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=60)  # type id (promotion, weekly…)
    competitors = models.CharField(max_length=200, default="All")
    period = models.CharField(max_length=80, blank=True)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.GENERATING)
    generated_at = models.DateTimeField(null=True, blank=True)
    generated_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    config = models.JSONField(default=dict, blank=True)  # type title, category, metrics…
    summary = models.TextField(blank=True)  # AI narrative
    file_ref = models.CharField(max_length=300, blank=True)  # PDF/export (scaffold)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["workspace", "-created_at"])]

    def __str__(self):
        return self.title


class ReportSchedule(models.Model):
    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="report_schedules"
    )
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=60)
    competitors = models.CharField(max_length=200, default="All competitors")
    frequency = models.CharField(max_length=40, default="Every day")
    run_time = models.CharField(max_length=10, default="08:00")
    enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    recipients = models.JSONField(default=list, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
