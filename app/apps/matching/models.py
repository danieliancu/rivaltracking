"""Product matching results.

A ProductListing (a competitor's offer) is linked to a canonical Product. The
MatchResult records how the link was made and how confident we are, so
high-confidence deterministic matches auto-apply while ambiguous ones stay
reviewable.
"""
from django.db import models

from apps.core.scoping import WorkspaceManager


class MatchResult(models.Model):
    class Method(models.TextChoices):
        GTIN = "gtin", "GTIN/EAN/UPC"
        MPN = "mpn", "MPN + brand"
        SKU = "sku", "Exact SKU"
        BRAND_MODEL = "brand_model", "Brand + model"
        TITLE = "title", "Title similarity"
        NONE = "none", "No match"

    class Status(models.TextChoices):
        AUTO_MATCHED = "auto_matched", "Auto matched"
        REVIEW_REQUIRED = "review_required", "Review required"
        UNMATCHED = "unmatched", "Unmatched"
        REJECTED = "rejected", "Rejected"
        MANUALLY_CONFIRMED = "manually_confirmed", "Manually confirmed"

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="match_results"
    )
    listing = models.OneToOneField(
        "catalogue.ProductListing", on_delete=models.CASCADE, related_name="match_result"
    )
    product = models.ForeignKey(
        "catalogue.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="match_results",
    )
    confidence = models.FloatField(default=0.0)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.NONE)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.UNMATCHED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-confidence"]
        indexes = [
            models.Index(fields=["workspace", "status"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.listing} → {self.product} ({self.confidence:.0f}% {self.method})"
