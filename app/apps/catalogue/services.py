"""Change-aware history writes for listings.

Snapshots are only written when the value actually changed (or no snapshot
exists yet), so identical values on every scan don't create meaningless rows
while charts still get every real movement.
"""
from __future__ import annotations

from django.utils import timezone

from .models import PriceSnapshot, Promotion, StockSnapshot


def record_price_snapshot(listing, *, now=None):
    if listing.current_price is None:
        return None
    now = now or timezone.now()
    last = (
        listing.price_snapshots.order_by("-captured_at")
        .values_list("price", flat=True)
        .first()
    )
    if last is not None and last == listing.current_price:
        return None
    return PriceSnapshot.objects.create(
        workspace=listing.workspace,
        listing=listing,
        price=listing.current_price,
        currency=listing.currency,
        captured_at=now,
    )


def record_stock_snapshot(listing, *, now=None):
    now = now or timezone.now()
    last = (
        listing.stock_snapshots.order_by("-captured_at")
        .values_list("stock_status", flat=True)
        .first()
    )
    if last == listing.current_stock_status:
        return None
    return StockSnapshot.objects.create(
        workspace=listing.workspace,
        listing=listing,
        stock_status=listing.current_stock_status,
        quantity=listing.current_stock_quantity,
        captured_at=now,
    )


def sync_promotion(listing, *, now=None):
    """Open a Promotion row when one starts; close the active one when it ends."""
    now = now or timezone.now()
    active = listing.promotions.filter(active=True).order_by("-captured_at").first()
    current = listing.current_promotion or ""
    if current and (active is None or active.title != current):
        if active is not None:
            active.active = False
            active.ended_at = now
            active.save(update_fields=["active", "ended_at"])
        return Promotion.objects.create(
            workspace=listing.workspace,
            listing=listing,
            title=current,
            promotion_type="detected",
            value=current,
            started_at=now,
            active=True,
            captured_at=now,
        )
    if not current and active is not None:
        active.active = False
        active.ended_at = now
        active.save(update_fields=["active", "ended_at"])
    return None


def record_snapshots(listing, *, now=None):
    now = now or timezone.now()
    record_price_snapshot(listing, now=now)
    record_stock_snapshot(listing, now=now)
    sync_promotion(listing, now=now)
