"""Scan orchestration + evidence models.

ScanJob is the unit of work created by Run Scan / the beat dispatcher and
executed by Celery. DiscoveredUrl tracks the catalogue/product URLs found for a
competitor (so we don't rediscover forever and can detect removals safely).
RawCapture preserves bounded evidence for each fetched page so ChangeEvents can
reference where a change came from.
"""
from django.db import models

from apps.core.scoping import WorkspaceManager


class ScanJob(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        PARTIALLY_FAILED = "partially_failed", "Partially failed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    class Trigger(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        MANUAL = "manual", "Manual"
        INITIAL = "initial", "Initial"
        RETRY = "retry", "Retry"

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="scan_jobs"
    )
    competitor = models.ForeignKey(
        "competitors.Competitor", on_delete=models.CASCADE, related_name="scan_jobs"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    trigger_type = models.CharField(max_length=20, choices=Trigger.choices, default=Trigger.MANUAL)

    queued_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    products_found = models.PositiveIntegerField(default=0)
    products_updated = models.PositiveIntegerField(default=0)
    changes_detected = models.PositiveIntegerField(default=0)
    pages_requested = models.PositiveIntegerField(default=0)
    errors_count = models.PositiveIntegerField(default=0)
    error_summary = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-queued_at"]
        indexes = [
            models.Index(fields=["workspace", "-queued_at"]),
            models.Index(fields=["competitor", "-queued_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Scan {self.competitor} [{self.status}]"

    @property
    def is_active(self):
        return self.status in {self.Status.QUEUED, self.Status.RUNNING}

    @property
    def duration_seconds(self):
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None


class DiscoveredUrl(models.Model):
    class Kind(models.TextChoices):
        PRODUCT = "product", "Product"
        CATEGORY = "category", "Category"
        SITEMAP = "sitemap", "Sitemap"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        NEW = "new", "New"
        ACTIVE = "active", "Active"
        REMOVED = "removed", "Removed"
        IGNORED = "ignored", "Ignored"
        FAILED = "failed", "Failed"

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="discovered_urls"
    )
    competitor = models.ForeignKey(
        "competitors.Competitor", on_delete=models.CASCADE, related_name="discovered_urls"
    )
    url = models.CharField(max_length=800)
    url_hash = models.CharField(max_length=64)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.PRODUCT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    fail_count = models.PositiveIntegerField(default=0)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["url"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "competitor", "url_hash"],
                name="unique_discovered_url",
            )
        ]
        indexes = [
            models.Index(fields=["workspace", "competitor", "status"]),
            models.Index(fields=["url_hash"]),
        ]

    def __str__(self):
        return self.url


class RawCapture(models.Model):
    """Bounded evidence for a fetched page (retention-limited)."""

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="raw_captures"
    )
    scan_job = models.ForeignKey(
        ScanJob, on_delete=models.CASCADE, null=True, blank=True, related_name="captures"
    )
    competitor = models.ForeignKey(
        "competitors.Competitor",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="raw_captures",
    )
    url = models.CharField(max_length=800)
    http_status = models.PositiveIntegerField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)
    content_hash = models.CharField(max_length=64, blank=True)
    extraction = models.JSONField(default=dict, blank=True)
    snippet = models.TextField(blank=True)
    retained_until = models.DateTimeField(null=True, blank=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-fetched_at"]
        indexes = [
            models.Index(fields=["workspace", "-fetched_at"]),
            models.Index(fields=["content_hash"]),
        ]

    def __str__(self):
        return f"Capture {self.url} @ {self.fetched_at:%Y-%m-%d %H:%M}"
