"""Product-side workspace state: the watchlist.

Watchlist membership is shared across the Products and Changes pages. It is
scoped to the workspace (and optionally attributed to the user who added it).
"""
from django.db import models

from apps.core.scoping import WorkspaceManager


class WatchlistItem(models.Model):
    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="watchlist_items"
    )
    product = models.ForeignKey(
        "catalogue.Product", on_delete=models.CASCADE, related_name="watchlist_items"
    )
    added_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="watchlist_items",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "product"], name="unique_watchlist_product"
            )
        ]

    def __str__(self):
        return f"watch {self.product}"
