"""Alert mutations against the mock store (alerts-store.tsx semantics)."""
from datetime import date

from apps.core.mock.store import MockStore

from .data import ALERT_FORM_OPTIONS
from .selectors import TRIGGER_OPTIONS


def _unique_rule_id(rules, base):
    """alerts-store.tsx uniqueRuleId: appends -2, -3, ... until free."""
    if not any(r["id"] == base for r in rules):
        return base
    n = 2
    while any(r["id"] == f"{base}-{n}" for r in rules):
        n += 1
    return f"{base}-{n}"


def _form_fields(post):
    """Raw dialog fields with the create-alert-dialog.tsx defaults."""
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


def _build_rule(fields):
    """Derive the display strings the way the dialog's create() does, while
    keeping the raw trigger/operator/threshold fields on the rule."""
    trigger = TRIGGER_OPTIONS.get(fields["trigger_id"], TRIGGER_OPTIONS["price-decrease"])
    is_price = trigger["type_group"] == "price"
    is_pattern = fields["trigger_id"] == "related-changes"

    if is_price:
        condition = f"{trigger['label']} by {fields['operator']} {fields['threshold']}%"
    elif is_pattern:
        condition = (
            f"{fields['pattern_count']}+ related changes within "
            f"{fields['pattern_hours']} hours"
        )
    else:
        condition = trigger["label"]

    rule = {
        "name": (
            f"{trigger['label']} — {fields['product']}"
            if fields["product"]
            else f"{trigger['label']} — {fields['competitor']}"
        ),
        "type_group": trigger["type_group"],
        "condition": condition,
        "competitors": fields["competitor"],
        "frequency": fields["frequency"],
        "pattern_based": is_pattern,
        # Proper fields (not reverse-parsed like the prototype's mock model).
        "trigger_id": fields["trigger_id"],
        "operator": fields["operator"],
        "threshold": fields["threshold"],
        "pattern_count": fields["pattern_count"],
        "pattern_hours": fields["pattern_hours"],
        "brand": fields["brand"],
        "product": fields["product"],
    }
    if fields["category"] != ALERT_FORM_OPTIONS["categories"][0]:
        rule["category"] = fields["category"]
    if fields["priority"] != "low":
        rule["priority"] = fields["priority"]
    return rule


def create_rule(request, post):
    """Future: POST /api/alerts/rules"""
    store = MockStore(request)
    fields = _form_fields(post)
    rule = _build_rule(fields)
    rule.update(
        {
            "id": _unique_rule_id(
                store.get("alert_rules"),
                f"rule-{fields['trigger_id']}-{fields['threshold']}-{fields['category']}",
            ),
            "last_triggered": "Never",
            "active": True,
            "created_at": date.today().isoformat(),
        }
    )
    store.mutate("alert_rules", lambda rules: rules.insert(0, rule))
    return rule


def update_rule(request, rule_id, post):
    """Future: PATCH /api/alerts/rules/:id"""
    store = MockStore(request)
    existing = next((r for r in store.get("alert_rules") if r["id"] == rule_id), None)
    if existing is None:
        return None
    updated = _build_rule(_form_fields(post))
    updated.update(
        {
            "id": existing["id"],
            "name": existing["name"],
            "last_triggered": existing["last_triggered"],
            "active": existing["active"],
            "created_at": existing["created_at"],
        }
    )

    def _replace(rules):
        for i, r in enumerate(rules):
            if r["id"] == rule_id:
                rules[i] = updated

    store.mutate("alert_rules", _replace)
    return updated


def toggle_rule(request, rule_id):
    """Future: POST /api/alerts/rules/:id/toggle

    Returns the rule as it was BEFORE the flip (the toast copy depends on it).
    """
    store = MockStore(request)
    before = next((r for r in store.get("alert_rules") if r["id"] == rule_id), None)
    if before is None:
        return None
    before = dict(before)

    def _toggle(rules):
        for r in rules:
            if r["id"] == rule_id:
                r["active"] = not r["active"]

    store.mutate("alert_rules", _toggle)
    return before


def duplicate_rule(request, rule_id):
    """Future: POST /api/alerts/rules/:id/duplicate"""
    store = MockStore(request)
    rules = store.get("alert_rules")
    source = next((r for r in rules if r["id"] == rule_id), None)
    if source is None:
        return None
    copy = {
        **source,
        "id": _unique_rule_id(rules, f"{source['id']}-copy"),
        "name": f"{source['name']} (copy)",
        "last_triggered": "Never",
        "active": True,
        "created_at": date.today().isoformat(),
    }
    copy.pop("last_triggered_minutes", None)  # "Never" sorts last

    def _insert(items):
        items.insert(0, copy)

    store.mutate("alert_rules", _insert)
    return copy


def delete_rule(request, rule_id):
    """Future: DELETE /api/alerts/rules/:id

    Alerts already triggered by the rule are kept (recent_alerts untouched).
    """
    store = MockStore(request)
    name = next(
        (r["name"] for r in store.get("alert_rules") if r["id"] == rule_id), None
    )
    if name is None:
        return None
    store.replace(
        "alert_rules", [r for r in store.get("alert_rules") if r["id"] != rule_id]
    )
    return name


def mark_read(request, alert_id):
    """Future: POST /api/alerts/:id/read"""

    def _mark(alerts):
        for a in alerts:
            if a["id"] == alert_id:
                a["status"] = "viewed"

    MockStore(request).mutate("recent_alerts", _mark)


def mark_all_read(request):
    """Future: POST /api/alerts/read-all"""

    def _mark(alerts):
        for a in alerts:
            a["status"] = "viewed"

    MockStore(request).mutate("recent_alerts", _mark)
