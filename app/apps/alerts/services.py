"""Alert-rule mutations over the AlertRule/Alert models."""
from django.utils import timezone

from .data import ALERT_FORM_OPTIONS
from .models import Alert, AlertRule
from .selectors import TRIGGER_OPTIONS, _pk, rule_dict


def _workspace(request):
    return getattr(request, "workspace", None)


def _user(request):
    user = getattr(request, "user", None)
    return user if (user is not None and user.is_authenticated) else None


def _form_fields(post):
    return {
        "trigger_id": post.get("trigger") or "price-decrease",
        "operator": post.get("operator") or "more than",
        "threshold": post.get("threshold") or "10",
        "pattern_count": post.get("pattern_count") or "20",
        "pattern_hours": post.get("pattern_hours") or "6",
        "competitor": post.get("competitor") or ALERT_FORM_OPTIONS["competitors"][0],
        "category": post.get("category") or ALERT_FORM_OPTIONS["categories"][0],
        "brand": post.get("brand") or "",
        "product": post.get("product") or "",
        "priority": post.get("priority") or "medium",
        "frequency": post.get("frequency") or "Immediate",
    }


def _derive(fields):
    """Compute the display strings + model attrs from raw dialog fields."""
    trigger = TRIGGER_OPTIONS.get(fields["trigger_id"], TRIGGER_OPTIONS["price-decrease"])
    is_price = trigger["type_group"] == "price"
    is_pattern = fields["trigger_id"] == "related-changes"
    if is_price:
        condition = f"{trigger['label']} by {fields['operator']} {fields['threshold']}%"
    elif is_pattern:
        condition = f"{fields['pattern_count']}+ related changes within {fields['pattern_hours']} hours"
    else:
        condition = trigger["label"]
    name = (
        f"{trigger['label']} — {fields['product']}"
        if fields["product"]
        else f"{trigger['label']} — {fields['competitor']}"
    )
    config = {
        "trigger_id": fields["trigger_id"],
        "operator": fields["operator"],
        "threshold": fields["threshold"],
        "pattern_count": fields["pattern_count"],
        "pattern_hours": fields["pattern_hours"],
        "brand": fields["brand"],
        "product": fields["product"],
    }
    category = "" if fields["category"] == ALERT_FORM_OPTIONS["categories"][0] else fields["category"]
    return {
        "name": name,
        "type_group": trigger["type_group"],
        "condition": condition,
        "competitors": fields["competitor"],
        "frequency": fields["frequency"],
        "priority": fields["priority"],
        "pattern_based": is_pattern,
        "category": category,
        "config": config,
    }


def create_rule(request, post):
    """Future: POST /api/alerts/rules"""
    data = _derive(_form_fields(post))
    channels = ["in_app"]
    if (post.get("email_channel") or "").lower() in ("on", "1", "true"):
        channels.append("email")
    rule = AlertRule.objects.create(
        workspace=_workspace(request), created_by=_user(request), channels=channels, **data
    )
    return rule_dict(rule)


def update_rule(request, rule_id, post):
    """Future: PATCH /api/alerts/rules/:id — keeps the original name."""
    rule = AlertRule.objects.for_workspace(_workspace(request)).filter(pk=_pk(rule_id)).first()
    if rule is None:
        return None
    data = _derive(_form_fields(post))
    data.pop("name")  # preserve the original name, like the prototype
    for key, value in data.items():
        setattr(rule, key, value)
    rule.save()
    return rule_dict(rule)


def toggle_rule(request, rule_id):
    """Returns the rule dict as it was BEFORE the flip (for the toast copy)."""
    rule = AlertRule.objects.for_workspace(_workspace(request)).filter(pk=_pk(rule_id)).first()
    if rule is None:
        return None
    before = rule_dict(rule)
    rule.enabled = not rule.enabled
    rule.save(update_fields=["enabled", "updated_at"])
    return before


def duplicate_rule(request, rule_id):
    """Future: POST /api/alerts/rules/:id/duplicate"""
    source = AlertRule.objects.for_workspace(_workspace(request)).filter(pk=_pk(rule_id)).first()
    if source is None:
        return None
    copy = AlertRule.objects.create(
        workspace=source.workspace,
        created_by=_user(request),
        name=f"{source.name} (copy)",
        type_group=source.type_group,
        condition=source.condition,
        competitors=source.competitors,
        category=source.category,
        frequency=source.frequency,
        priority=source.priority,
        pattern_based=source.pattern_based,
        config=source.config,
        channels=source.channels,
    )
    return rule_dict(copy)


def delete_rule(request, rule_id):
    """Future: DELETE /api/alerts/rules/:id (fired Alerts are kept)."""
    rule = AlertRule.objects.for_workspace(_workspace(request)).filter(pk=_pk(rule_id)).first()
    if rule is None:
        return None
    name = rule.name
    rule.delete()
    return name


def mark_read(request, alert_id):
    """Future: POST /api/alerts/:id/read"""
    Alert.objects.for_workspace(_workspace(request)).filter(pk=_pk(alert_id)).update(
        status=Alert.Status.VIEWED, read_at=timezone.now()
    )


def mark_all_read(request):
    """Future: POST /api/alerts/read-all"""
    Alert.objects.for_workspace(_workspace(request)).filter(status=Alert.Status.NEW).update(
        status=Alert.Status.VIEWED, read_at=timezone.now()
    )
