"""Alert evaluation: turn ChangeEvents into Alerts via AlertRules.

Runs after change detection. Rule logic lives here (not in views). Delivery
failures never block detection.
"""
from __future__ import annotations

import re

from django.utils import timezone

from apps.changes.models import ChangeEvent

from .models import Alert, AlertRule

TRIGGER_TO_EVENT_TYPE = {
    "price-decrease": ChangeEvent.Type.PRICE_DECREASE,
    "price-increase": ChangeEvent.Type.PRICE_INCREASE,
    "stock-out": ChangeEvent.Type.STOCK_OUT,
    "stock-back": ChangeEvent.Type.STOCK_IN,
    "product-new": ChangeEvent.Type.PRODUCT_NEW,
    "product-removed": ChangeEvent.Type.PRODUCT_REMOVED,
    "promo-start": ChangeEvent.Type.PROMOTION_STARTED,
    "promo-end": ChangeEvent.Type.PROMOTION_ENDED,
}

EVENT_TYPE_GROUP = {
    ChangeEvent.Type.PRICE_INCREASE: "price",
    ChangeEvent.Type.PRICE_DECREASE: "price",
    ChangeEvent.Type.STOCK_IN: "stock",
    ChangeEvent.Type.STOCK_OUT: "stock",
    ChangeEvent.Type.PRODUCT_NEW: "products",
    ChangeEvent.Type.PRODUCT_REMOVED: "products",
    ChangeEvent.Type.PROMOTION_STARTED: "promotions",
    ChangeEvent.Type.PROMOTION_ENDED: "promotions",
    ChangeEvent.Type.PRODUCT_METADATA_CHANGE: "products",
}


def _pct(secondary):
    if not secondary:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", secondary)
    return abs(float(m.group())) if m else None


def rule_matches(rule, event):
    cfg = rule.config or {}
    expected = TRIGGER_TO_EVENT_TYPE.get(cfg.get("trigger_id"))
    if expected:
        if event.event_type != expected:
            return False
    else:
        # Rules without a specific trigger id match by type group.
        if rule.type_group and EVENT_TYPE_GROUP.get(event.event_type) != rule.type_group:
            return False
    if rule.competitors and rule.competitors != "All competitors":
        if event.competitor.name != rule.competitors:
            return False
    if rule.category and event.product and event.product.category != rule.category:
        return False
    if rule.type_group == "price":
        threshold = float(cfg.get("threshold") or 0)
        pct = _pct(event.secondary)
        if pct is not None and threshold and pct < threshold:
            return False
    return True


def build_payload(rule, event):
    product = event.product
    return {
        "product": product.name if product else "",
        "product_slug": product.slug if product else "",
        "competitor": event.competitor.name,
        "event": f"{event.label}{(' ' + event.secondary) if event.secondary else ''}",
        "kind": event.kind,
        "priority": rule.priority,
        "detected_at": timezone.localtime(event.detected_at).strftime("%d %b, %H:%M"),
        "rule": {
            "condition": rule.condition,
            "detected": event.secondary or event.new_value,
            "scope": rule.competitors,
        },
        "rule_id": str(rule.pk),
        "rule_name": rule.name,
        "ai_note": "",
        "evidence": {
            "category": product.category if product else "",
            "change": event.secondary,
            "current": event.new_value,
            "previous": event.previous_value,
            "difference": event.difference,
            "stock": event.new_value if event.event_type in (ChangeEvent.Type.STOCK_IN, ChangeEvent.Type.STOCK_OUT) else "",
        },
    }


def evaluate_event(event):
    """Create Alerts for every matching enabled rule (idempotent per event/rule)."""
    created = []
    rules = AlertRule.objects.for_workspace(event.workspace).filter(enabled=True)
    for rule in rules:
        if rule.pattern_based or not rule_matches(rule, event):
            continue
        if Alert.objects.filter(workspace=event.workspace, rule=rule, change_event=event).exists():
            continue
        alert = Alert.objects.create(
            workspace=event.workspace,
            rule=rule,
            change_event=event,
            status=Alert.Status.NEW,
            title=f"{rule.name}",
            message=f"{event.competitor.name}: {event.label}",
            payload=build_payload(rule, event),
        )
        AlertRule.objects.filter(id=rule.id).update(last_triggered_at=timezone.now())
        created.append(alert)
    return created


def evaluate_events(events):
    from .delivery import deliver

    total = 0
    for event in events:
        try:
            for alert in evaluate_event(event):
                deliver(alert)  # delivery failures are isolated inside deliver()
                total += 1
        except Exception:  # a rule failure never breaks detection
            continue
    return total
