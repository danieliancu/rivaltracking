"""Alerts page reads: rule filtering/sorting, notification annotation,
chart payloads and dialog form state (ports of alert-rules-table.tsx,
recent-alerts-table.tsx, create-alert-dialog.tsx and alerts.tsx logic)."""
import json
import sys
from django.utils import timezone
from django.utils.safestring import mark_safe

from apps.competitors import selectors as competitor_selectors
from apps.core.entities import slugify
from apps.core.format import relative_time
from apps.products import selectors as product_selectors

from .models import Alert, AlertRule

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


def _workspace(request):
    return getattr(request, "workspace", None)


def _pk(value):
    """Integer pk or None for non-numeric ids (so bad ids 404, not error)."""
    return int(value) if str(value).isdigit() else None


def kpi_cards(request):
    ws = _workspace(request)
    rules = AlertRule.objects.for_workspace(ws)
    alerts = Alert.objects.for_workspace(ws)
    values = {
        "active": rules.filter(enabled=True).count(),
        "triggered": alerts.filter(triggered_at__date=timezone.localdate()).count(),
        "high": alerts.filter(payload__priority="high", status=Alert.Status.NEW).count(),
        "covered": len(competitor_selectors.header_list(request)),
    }
    return [
        {
            "icon": KPI_ICONS.get(k["id"], "bell"),
            "tone": k["tone"],
            "value": str(values.get(k["id"], k["value"])),
            "label": k["label"],
        }
        for k in ALERT_KPIS
    ]


# ---------------------------------------------------------------------------
# Alert rules


def rule_dict(obj, now=None):
    now = now or timezone.now()
    cfg = obj.config or {}
    if obj.last_triggered_at:
        mins = max(0, int((now - obj.last_triggered_at).total_seconds() // 60))
        last = relative_time(mins)
    else:
        mins, last = None, "Never"
    d = {
        "id": str(obj.pk),
        "name": obj.name,
        "type_group": obj.type_group,
        "condition": obj.condition,
        "competitors": obj.competitors,
        "frequency": obj.frequency,
        "active": obj.enabled,
        "priority": obj.priority,
        "created_at": obj.created_at.date().isoformat(),
        "last_triggered": last,
        "last_triggered_minutes": mins,
        "pattern_based": obj.pattern_based,
        "trigger_id": cfg.get("trigger_id"),
        "operator": cfg.get("operator"),
        "threshold": cfg.get("threshold"),
        "pattern_count": cfg.get("pattern_count"),
        "pattern_hours": cfg.get("pattern_hours"),
        "brand": cfg.get("brand", ""),
        "product": cfg.get("product", ""),
    }
    if obj.category:
        d["category"] = obj.category
    return d


def all_rules(request):
    now = timezone.now()
    return [rule_dict(r, now) for r in AlertRule.objects.for_workspace(_workspace(request))]


def rule_by_id(request, rule_id):
    obj = AlertRule.objects.for_workspace(_workspace(request)).filter(pk=_pk(rule_id)).first()
    return rule_dict(obj) if obj else None


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
        "triggered": lambda r: r["last_triggered_minutes"] if r.get("last_triggered_minutes") is not None else sys.maxsize,
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


def alert_dict(obj, now=None):
    now = now or timezone.now()
    mins = max(0, int((now - obj.triggered_at).total_seconds() // 60))
    return {
        **(obj.payload or {}),
        "id": obj.pk,
        "status": obj.status,
        "triggered": relative_time(mins),
    }


def all_recent(request):
    now = timezone.now()
    return [alert_dict(a, now) for a in Alert.objects.for_workspace(_workspace(request))]


def alert_by_id(request, alert_id):
    obj = Alert.objects.for_workspace(_workspace(request)).filter(pk=_pk(alert_id)).first()
    return alert_dict(obj) if obj else None


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
