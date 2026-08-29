"""Competitor discovery candidates (real, workspace-scoped)."""
from django.db import models

from apps.core.scoping import WorkspaceManager


class DiscoveryCandidate(models.Model):
    class Status(models.TextChoices):
        SUGGESTED = "suggested", "Suggested"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        MONITORING = "monitoring", "Monitoring"
        DISMISSED = "dismissed", "Dismissed"

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="discovery_candidates"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    domain = models.CharField(max_length=255, blank=True)
    website_url = models.URLField(blank=True)
    score = models.PositiveIntegerField(default=0)
    tone = models.CharField(max_length=20, blank=True)
    cluster = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUGGESTED)
    reasons = models.JSONField(default=list, blank=True)
    catalogue_profile = models.JSONField(default=dict, blank=True)
    discovered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-score", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "slug"], name="unique_discovery_candidate_slug"
            )
        ]
        indexes = [models.Index(fields=["workspace", "status"])]

    def __str__(self):
        return f"{self.name} ({self.score}%)"
