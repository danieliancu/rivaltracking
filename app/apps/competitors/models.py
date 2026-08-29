"""Competitor model — a monitored competitor site within a workspace.

Headline metric columns (products_count, changes_today, price_drops, …) are
denormalised presentational values: in Phase 3 the engine recomputes them from
listings and change events over a window, but for Phase 2 they are seeded so
the UI keeps its exact numbers. Structural data (listings, history, events)
lives in real related tables.
"""
from django.db import models
from django.utils import timezone

from apps.core.scoping import WorkspaceManager


class Competitor(models.Model):
    class Status(models.TextChoices):
        HEALTHY = "healthy", "Healthy"
        ATTENTION = "attention", "Attention"
        SCANNING = "scanning", "Scanning"
        INITIALISING = "initialising", "Initialising"
        PAUSED = "paused", "Paused"
        BLOCKED = "blocked", "Protected"

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="competitors"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    website_url = models.URLField(blank=True)
    domain = models.CharField(max_length=255, blank=True)
    market = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.INITIALISING
    )
    monitoring_enabled = models.BooleanField(default=True)
    note = models.CharField(max_length=300, blank=True)
    tone = models.CharField(max_length=20, blank=True)

    # Denormalised headline metrics (see module docstring).
    products_count = models.PositiveIntegerField(null=True, blank=True)
    changes_today = models.PositiveIntegerField(null=True, blank=True)
    price_drops = models.PositiveIntegerField(null=True, blank=True)
    price_increases = models.PositiveIntegerField(null=True, blank=True)
    stock_changes = models.PositiveIntegerField(null=True, blank=True)

    # Monitoring config (formerly the competitor_configs mock collection).
    monitoring_frequency = models.CharField(max_length=50, default="Every 24 hours")
    track_prices = models.BooleanField(default=True)
    track_stock = models.BooleanField(default=True)
    track_products = models.BooleanField(default=True)
    track_promotions = models.BooleanField(default=True)

    added_at = models.DateField(default=timezone.localdate)
    last_scan_at = models.DateTimeField(null=True, blank=True)
    next_scan_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "slug"],
                name="unique_competitor_slug_per_workspace",
            ),
            models.UniqueConstraint(
                fields=["workspace", "domain"],
                condition=~models.Q(domain=""),
                name="unique_competitor_domain_per_workspace",
            ),
        ]
        indexes = [
            models.Index(fields=["workspace", "status"]),
        ]

    def __str__(self):
        return self.name
