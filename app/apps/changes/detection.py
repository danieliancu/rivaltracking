"""Deterministic change detection.

Compares a listing's previous persisted state with its new normalised state and
emits idempotent ChangeEvents. Detection is separate from significance (impact)
and from AI (interpretation).
"""
from __future__ import annotations

from decimal import Decimal

from apps.catalogue.models import StockStatus
from apps.core.format import gbp

from . import significance
from .models import ChangeEvent


def _pct(old: Decimal, new: Decimal):
    if not old:
        return None
    return round(float((new - old) / old * 100), 1)


def _record(*, workspace, competitor, listing, product, event_type, kind, label,
            previous, new, secondary="", secondary_tone="", difference="", pct=None,
            detected_at, capture_id=None):
    """Idempotently create a ChangeEvent (dedupe by listing+type+value+day)."""
    if ChangeEvent.objects.filter(
        workspace=workspace,
        listing=listing,
        event_type=event_type,
        new_value=new,
        detected_at__date=detected_at.date(),
    ).exists():
        return None
    return ChangeEvent.objects.create(
        workspace=workspace,
        competitor=competitor,
        listing=listing,
        product=product,
        event_type=event_type,
        kind=kind,
        label=label,
        previous_value=previous,
        new_value=new,
        secondary=secondary,
        secondary_tone=secondary_tone,
        impact=significance.impact_for(event_type, pct=pct),
        difference=difference,
        detected_at=detected_at,
        metadata={"capture_id": capture_id} if capture_id else {},
    )


def detect_for_listing(listing, previous, *, detected_at, capture_id=None, is_new=False):
    """Return the list of ChangeEvents created for one listing transition.

    ``previous`` is the pre-update snapshot dict (price/stock/promotion/title/
    category) or None for a brand-new listing.
    """
    ws = listing.workspace
    competitor = listing.competitor
    product = listing.product
    events = []
    T = ChangeEvent.Type

    if is_new or previous is None:
        ev = _record(
            workspace=ws, competitor=competitor, listing=listing, product=product,
            event_type=T.PRODUCT_NEW, kind="new", label="New product",
            previous="", new=listing.competitor_product_name or (product.name if product else ""),
            detected_at=detected_at, capture_id=capture_id,
        )
        return [ev] if ev else []

    # Price
    old_price, new_price = previous.get("price"), listing.current_price
    if old_price is not None and new_price is not None and old_price != new_price:
        pct = _pct(old_price, new_price)
        decrease = new_price < old_price
        ev = _record(
            workspace=ws, competitor=competitor, listing=listing, product=product,
            event_type=T.PRICE_DECREASE if decrease else T.PRICE_INCREASE,
            kind="drop" if decrease else "increase",
            label="Price decrease" if decrease else "Price increase",
            previous=gbp(old_price), new=gbp(new_price),
            secondary=f"{pct:+.1f}%" if pct is not None else "",
            secondary_tone="success" if decrease else "danger",
            difference=f"{'-' if decrease else '+'}{gbp(abs(new_price - old_price)).lstrip('-')}"
            if new_price is not None else "",
            pct=pct, detected_at=detected_at, capture_id=capture_id,
        )
        if ev:
            events.append(ev)

    # Stock
    old_stock, new_stock = previous.get("stock"), listing.current_stock_status
    if old_stock != new_stock:
        if new_stock == StockStatus.OUT_OF_STOCK:
            ev = _record(workspace=ws, competitor=competitor, listing=listing, product=product,
                         event_type=T.STOCK_OUT, kind="oos", label="Out of stock",
                         previous="In stock", new="Out of stock",
                         detected_at=detected_at, capture_id=capture_id)
            if ev:
                events.append(ev)
        elif new_stock == StockStatus.IN_STOCK and old_stock == StockStatus.OUT_OF_STOCK:
            ev = _record(workspace=ws, competitor=competitor, listing=listing, product=product,
                         event_type=T.STOCK_IN, kind="back", label="Back in stock",
                         previous="Out of stock", new="In stock",
                         detected_at=detected_at, capture_id=capture_id)
            if ev:
                events.append(ev)

    # Promotion
    old_promo, new_promo = previous.get("promotion") or "", listing.current_promotion or ""
    if old_promo != new_promo:
        if new_promo:
            ev = _record(workspace=ws, competitor=competitor, listing=listing, product=product,
                         event_type=T.PROMOTION_STARTED, kind="promo", label="Promotion started",
                         previous="No promotion", new=new_promo,
                         detected_at=detected_at, capture_id=capture_id)
        else:
            ev = _record(workspace=ws, competitor=competitor, listing=listing, product=product,
                         event_type=T.PROMOTION_ENDED, kind="promo-end", label="Promotion ended",
                         previous=old_promo, new="No promotion",
                         detected_at=detected_at, capture_id=capture_id)
        if ev:
            events.append(ev)

    return events


def record_removed(listing, *, detected_at):
    ev = _record(
        workspace=listing.workspace, competitor=listing.competitor, listing=listing,
        product=listing.product, event_type=ChangeEvent.Type.PRODUCT_REMOVED,
        kind="removed", label="Removed",
        previous=listing.competitor_product_name or "", new="Removed",
        detected_at=detected_at,
    )
    return [ev] if ev else []
