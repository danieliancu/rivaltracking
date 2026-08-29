"""Persistent change events.

Phase 3's change-detection engine writes rows here by diffing successive
snapshots. Phase 2 seeds them so the Changes UI reads real rows. The UI's
short ``kind`` token and rich display strings (detected_at label, evidence,
ai_note) live alongside the canonical ``event_type`` — kind maps many-to-one
onto event_type (e.g. drop → price_decrease).
"""
from django.db import models

from apps.core.scoping import WorkspaceManager


class ChangeEvent(models.Model):
    class Type(models.TextChoices):
        PRICE_INCREASE = "price_increase", "Price increase"
        PRICE_DECREASE = "price_decrease", "Price decrease"
        STOCK_IN = "stock_in", "Stock in"
        STOCK_OUT = "stock_out", "Stock out"
        PRODUCT_NEW = "product_new", "New product"
        PRODUCT_REMOVED = "product_removed", "Removed product"
        PROMOTION_STARTED = "promotion_started", "Promotion started"
        PROMOTION_ENDED = "promotion_ended", "Promotion ended"
        PRODUCT_METADATA_CHANGE = "product_metadata_change", "Product metadata change"

    class Impact(models.TextChoices):
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="change_events"
    )
    competitor = models.ForeignKey(
        "competitors.Competitor", on_delete=models.CASCADE, related_name="change_events"
    )
    product = models.ForeignKey(
        "catalogue.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_events",
    )
    listing = models.ForeignKey(
        "catalogue.ProductListing",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_events",
    )

    event_type = models.CharField(max_length=40, choices=Type.choices)
    kind = models.CharField(max_length=20)
    label = models.CharField(max_length=60)
    previous_value = models.CharField(max_length=200, blank=True)
    new_value = models.CharField(max_length=200, blank=True)
    secondary = models.CharField(max_length=60, blank=True)
    secondary_tone = models.CharField(max_length=20, blank=True)
    impact = models.CharField(
        max_length=10, choices=Impact.choices, default=Impact.MEDIUM
    )
    difference = models.CharField(max_length=40, blank=True)

    # Presentational extras that don't warrant their own columns: evidence
    # snapshot, ai_note, the "Today, 11:42"-style display strings, source_url.
    metadata = models.JSONField(default=dict, blank=True)

    detected_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-detected_at"]
        indexes = [
            models.Index(fields=["workspace", "-detected_at"]),
            models.Index(fields=["workspace", "event_type"]),
            models.Index(fields=["competitor", "-detected_at"]),
        ]

    def __str__(self):
        return f"{self.label} — {self.competitor} @ {self.detected_at:%Y-%m-%d %H:%M}"
