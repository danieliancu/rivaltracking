"""Alerts page reads: rule filtering/sorting, notification annotation,
chart payloads and dialog form state (ports of alert-rules-table.tsx,
recent-alerts-table.tsx, create-alert-dialog.tsx and alerts.tsx logic)."""
import json
import sys
from django.utils.safestring import mark_safe

from apps.competitors import selectors as competitor_selectors
from apps.core.entities import slugify
from apps.core.store import WorkspaceStore
from apps.products import selectors as product_selectors

from .data import (
    ALERT_ACTIVITY,
    ALERT_COVERAGE,
    ALERT_FILTER_OPTIONS,
    ALERT_FORM_OPTIONS,
    ALERT_KPIS,
    ALERT_TRIGGER_GROUPS,
    KIND_TO_TRIGGER,
    MOST_TRIGGERED_RULES,
    TYPE_GROUP_META,
)

# alerts.tsx kpiIcons
KPI_ICONS = {
    "active": "bell",
    "triggered": "bell-ring",
    "high": "triangle-alert",
    "covered": "users",
}

# recent-alerts-table.tsx productIcons (fallback Package)
ALERT_PRODUCT_ICONS = {
    "lego-castle-set": "blocks",
    "stem-robot-kit": "bot",
    "wooden-balance-bike": "bike",
    "stem-coding-kit": "bot",
    "garden-water-table": "baby",
}

# create-alert-dialog.tsx triggerByTypeGroup (edit-mode fallback)
TRIGGER_BY_TYPE_GROUP = {
    "price": "price-decrease",
    "stock": "stock-out",
    "products": "product-new",
    "promotions": "promo-start",
    "patterns": "related-changes",
}

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

# Flat trigger catalogue: id -> {label, type_group}
TRIGGER_OPTIONS = {
    o["id"]: {"label": o["label"], "type_group": g["type_group"]}
    for g in ALERT_TRIGGER_GROUPS
    for o in g["options"]
}

ACTIVITY_RANGES = [
    {"key": "today", "label": "Today"},
    {"key": "7d", "label": "7D"},
    {"key": "30d", "label": "30D"},
]
ACTIVITY_DATA_KEY = {"today": "Today", "7d": "7D", "30d": "30D"}

# Same escaping as Django's json_script, for embedding state in <script> tags.
_JSON_ESCAPES = {ord(">"): "\\u003E", ord("<"): "\\u003C", ord("&"): "\\u0026"}


def kpi_cards():
    return [
        {
            "icon": KPI_ICONS.get(k["id"], "bell"),
            "tone": k["tone"],
            "value": k["value"],
            "label": k["label"],
        }
        for k in ALERT_KPIS
    ]


# ---------------------------------------------------------------------------
# Alert rules


def all_rules(request):
    return WorkspaceStore(request).get("alert_rules")


def rule_by_id(request, rule_id):
    for rule in all_rules(request):
        if rule["id"] == rule_id:
            return rule
    return None


def parse_rule_filters(params):
    return {
        "q": params.get("q", ""),
        "status": params.get("status") or "all",
        "type": params.get("type") or "all",
        "competitor": params.get("competitor") or "All competitors",
        "sort": params.get("sort") or "triggered",
    }


def visible_rules(rules, filters):
    """alert-rules-table.tsx `visible` memo: filter then sort."""
    q = filters["q"].strip().lower()
    out = [
        r
        for r in rules
        if (not q or q in r["name"].lower() or q in r["condition"].lower())
        and (
            filters["status"] == "all"
            or (r["active"] if filters["status"] == "active" else not r["active"])
        )
        and (filters["type"] == "all" or r["type_group"] == filters["type"])
        and (
            filters["competitor"] == "All competitors"
            or r["competitors"] == filters["competitor"]
        )
    ]
    sorters = {
        "triggered": lambda r: r.get("last_triggered_minutes", sys.maxsize),
        "created": lambda r: _desc_str(r["created_at"]),
        "priority": lambda r: PRIORITY_RANK[r.get("priority") or "low"],
        "name": lambda r: r["name"],
    }
    return sorted(out, key=sorters[filters["sort"]])


class _desc_str(str):
    """Reverse-ordering wrapper so string sorts can descend inside sorted()."""

    def __lt__(self, other):
        return str.__gt__(self, other)


def with_meta(rules):
    return [{**r, "meta": TYPE_GROUP_META[r["type_group"]]} for r in rules]


def competitor_filter_options(request):
    names = [c["name"] for c in competitor_selectors.header_list(request)]
    return ["All competitors", *names]


# ---------------------------------------------------------------------------
# Recent alerts


def all_recent(request):
    return WorkspaceStore(request).get("recent_alerts")


def alert_by_id(request, alert_id):
    for alert in all_recent(request):
        if alert["id"] == alert_id:
            return alert
    return None


def recent_context(request, rule_param):
    """Rows (optionally filtered by rule id) annotated for the SubjectCell."""
    alerts = all_recent(request)
    rule_filter = None
    if rule_param:
        rule = rule_by_id(request, rule_param)
        rule_filter = {"id": rule_param, "name": rule["name"] if rule else rule_param}
        alerts = [a for a in alerts if a["rule_id"] == rule_param]
    rows = [
        {**a, "product_icon": ALERT_PRODUCT_ICONS.get(a.get("product_slug", ""), "package")}
        for a in alerts
    ]
    return {"recent_alerts": rows, "rule_filter": rule_filter}


def drawer_context(request, alert):
    """alert-detail-drawer.tsx derived values."""
    product = None
    if alert.get("product_slug"):
        product = product_selectors.by_slug(request, alert["product_slug"])
    return {
        "alert": alert,
        "source_url": product.get("source_url") if product else None,
        "competitor_slug": slugify(alert["competitor"]),
    }


# ---------------------------------------------------------------------------
# Charts


def activity_payload(range_key):
    points = ALERT_ACTIVITY[ACTIVITY_DATA_KEY.get(range_key, "7D")]
    series = [
        ("price", "Price", "chart-1"),
        ("stock", "Stock", "warning"),
        ("product", "Products", "chart-2"),
        ("promotions", "Promotions", "purple"),
    ]
    return {
        "type": "line",
        "labels": [p["label"] for p in points],
        "series": [
            {"label": label, "data": [p[key] for p in points], "color": color}
            for key, label, color in series
        ],
        "options": {},
    }


def most_triggered_payload():
    return {
        "type": "hbar",
        "labels": [r["name"] for r in MOST_TRIGGERED_RULES],
        "series": [{"data": [r["count"] for r in MOST_TRIGGERED_RULES], "color": "chart-1"}],
        "options": {"labels": True, "barSize": 14, "labelWidth": 140},
    }


def coverage_items():
    icons = ["bell", "boxes", "folder-search", "triangle-alert"]
    tones = ["text-info", "text-teal", "text-purple", "text-warning"]
    return [
        {**stat, "icon": icons[i], "tone": tones[i]}
        for i, stat in enumerate(ALERT_COVERAGE)
    ]


# ---------------------------------------------------------------------------
# Create/edit dialog form state


def _default_form():
    return {
        "trigger_id": "price-decrease",
        "operator": "more than",
        "threshold": "10",
        "pattern_count": "20",
        "pattern_hours": "6",
        "competitor": ALERT_FORM_OPTIONS["competitors"][0],
        "category": ALERT_FORM_OPTIONS["categories"][0],
        "brand": "",
        "product": "",
        "priority": "medium",
        "frequency": "Immediate",
    }


def _resolve_trigger(token):
    """Accept a trigger id directly, or a Changes-page kind token."""
    if token in TRIGGER_OPTIONS:
        return token
    return KIND_TO_TRIGGER.get(token)


def form_state(rule=None, prefill=None):
    """create-alert-dialog.tsx open effect: edit-mode mapping or prefill."""
    state = _default_form()
    if rule:
        if rule.get("trigger_id"):
            # Rules created here store the form fields directly.
            for key in state:
                if rule.get(key) is not None:
                    state[key] = rule[key]
            state["brand"] = rule.get("brand", "")
            state["product"] = rule.get("product", "")
        else:
            # Seed rules: recover form values from the condition string,
            # mirroring the prototype's best-effort parsing.
            condition = rule["condition"].lower()
            type_group = rule["type_group"]
            if type_group == "price" and "increase" in condition:
                state["trigger_id"] = "price-increase"
            elif type_group == "stock" and "back" in condition:
                state["trigger_id"] = "stock-back"
            elif type_group == "products" and "removed" in condition:
                state["trigger_id"] = "product-removed"
            else:
                state["trigger_id"] = TRIGGER_BY_TYPE_GROUP[type_group]
            import re

            pct = re.search(r"(\d+)\s*%", rule["condition"])
            if pct:
                state["threshold"] = pct.group(1)
            state["operator"] = "less than" if "less than" in condition else "more than"
            if rule["competitors"] in ALERT_FORM_OPTIONS["competitors"]:
                state["competitor"] = rule["competitors"]
        state["category"] = rule.get("category") or ALERT_FORM_OPTIONS["categories"][0]
        state["priority"] = rule.get("priority") or "low"
        state["frequency"] = rule["frequency"]
    elif prefill:
        trigger = _resolve_trigger(prefill.get("trigger", ""))
        if trigger:
            state["trigger_id"] = trigger
        competitor = prefill.get("competitor", "")
        if competitor in ALERT_FORM_OPTIONS["competitors"]:
            state["competitor"] = competitor
        category = prefill.get("category", "")
        if category in ALERT_FORM_OPTIONS["categories"]:
            state["category"] = category
        state["product"] = prefill.get("product", "")
    return state


def form_state_json(state):
    """Alpine initial state (+ trigger catalogue), escaped like json_script."""
    payload = {
        "triggerId": state["trigger_id"],
        "operator": state["operator"],
        "threshold": state["threshold"],
        "patternCount": state["pattern_count"],
        "patternHours": state["pattern_hours"],
        "competitor": state["competitor"],
        "category": state["category"],
        "brand": state["brand"],
        "product": state["product"],
        "priority": state["priority"],
        "frequency": state["frequency"],
        "triggers": TRIGGER_OPTIONS,
    }
    return mark_safe(json.dumps(payload).translate(_JSON_ESCAPES))


def dialog_context(request, rule=None, prefill=None):
    state = form_state(rule=rule, prefill=prefill)
    return {
        "edit_rule": rule,
        "form": state,
        "form_json": form_state_json(state),
        "trigger_groups": ALERT_TRIGGER_GROUPS,
        "form_options": ALERT_FORM_OPTIONS,
        "filter_options": ALERT_FILTER_OPTIONS,
    }
