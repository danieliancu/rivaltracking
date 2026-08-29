"""Significance rules — kept separate from detection.

Detection answers "what changed"; significance answers "how important" (impact
high/medium/low) and "is this worth an AI analysis". AI later answers "why it
matters". Deterministic and cheap.
"""
from __future__ import annotations

from .models import ChangeEvent

_HIGH = ChangeEvent.Impact.HIGH
_MED = ChangeEvent.Impact.MEDIUM
_LOW = ChangeEvent.Impact.LOW


def impact_for(event_type, *, pct=None) -> str:
    """Impact from event type + magnitude (percentage change where relevant)."""
    T = ChangeEvent.Type
    if event_type in (T.PRICE_DECREASE, T.PRICE_INCREASE):
        magnitude = abs(pct or 0)
        if magnitude >= 15:
            return _HIGH
        if magnitude >= 5:
            return _MED
        return _LOW
    if event_type in (T.STOCK_OUT, T.PRODUCT_REMOVED, T.PROMOTION_STARTED):
        return _HIGH
    if event_type in (T.STOCK_IN, T.PRODUCT_NEW, T.PROMOTION_ENDED):
        return _MED
    return _LOW


# The funnel that decides which events get an (expensive) AI analysis.
AI_ELIGIBLE_TYPES = {
    ChangeEvent.Type.PRICE_DECREASE,
    ChangeEvent.Type.PRICE_INCREASE,
    ChangeEvent.Type.STOCK_OUT,
    ChangeEvent.Type.PRODUCT_REMOVED,
    ChangeEvent.Type.PROMOTION_STARTED,
}


def is_ai_eligible(event) -> bool:
    """Only meaningful, high/medium-impact events are worth AI interpretation."""
    return (
        event.event_type in AI_ELIGIBLE_TYPES
        and event.impact in (_HIGH, _MED)
    )
