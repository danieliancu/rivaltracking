from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_POST

from apps.ai import insights as ai_insights

from . import selectors, services
from .data import ALERT_FILTER_OPTIONS


def _rules_context(request, params):
    filters = selectors.parse_rule_filters(params)
    rules = selectors.all_rules(request)
    return {
        "filters": filters,
        "filter_options": ALERT_FILTER_OPTIONS,
        "competitor_options": selectors.competitor_filter_options(request),
        "rules_total": len(rules),
        "rules": selectors.with_meta(selectors.visible_rules(rules, filters)),
    }


def _recent_context(request, params):
    return selectors.recent_context(request, params.get("rule") or None)


def _activity_context(request, params):
    range_key = params.get("activity_range") or "7d"
    if range_key not in selectors.ACTIVITY_DATA_KEY:
        range_key = "7d"
    return {
        "activity_range": range_key,
        "activity_ranges": selectors.ACTIVITY_RANGES,
        "activity_chart": selectors.activity_payload(request, range_key),
    }


def index(request):
    context = {
        "kpis": selectors.kpi_cards(request),
        **_rules_context(request, request.GET),
        **_recent_context(request, request.GET),
        **_activity_context(request, request.GET),
        "most_triggered_chart": selectors.most_triggered_payload(request),
        "coverage": selectors.coverage_items(request),
        "ai_summary": ai_insights.activity_summary(request.workspace),
    }

    htmx = getattr(request, "htmx", None)
    if htmx and htmx.target == "alert-rules-fragment":
        return render(request, "alerts/partials/rules_table.html", context)
    if htmx and htmx.target == "recent-alerts-fragment":
        return render(request, "alerts/partials/recent_table.html", context)
    if htmx and htmx.target == "alert-activity-fragment":
        return render(request, "alerts/partials/activity_card.html", context)

    # Deep link: /alerts?create=1&trigger=…&competitor=…&category=…&product=…
    if request.GET.get("create"):
        context["open_dialog"] = True
        context.update(selectors.dialog_context(request, prefill=request.GET))
    return render(request, "alerts/index.html", context)


def rule_dialog(request):
    """Create/edit dialog fragment (HTMX → #modal-root)."""
    rule = None
    rule_id = request.GET.get("rule")
    if rule_id:
        rule = selectors.rule_by_id(request, rule_id)
    return render(
        request,
        "alerts/partials/rule_dialog.html",
        selectors.dialog_context(request, rule=rule),
    )


def _rules_response(request, toast):
    """Refreshed rules-table fragment + OOB toast, keeping active filters
    (row actions post the filter form along via hx-include)."""
    context = {**_rules_context(request, request.POST), **toast}
    return render(request, "alerts/partials/rules_response.html", context)


@require_POST
def create_rule(request):
    rule = services.create_rule(request, request.POST)
    return _rules_response(
        request,
        {"toast_variant": "success", "toast_title": "Alert created", "toast_description": rule["name"]},
    )


@require_POST
def update_rule(request, rule_id):
    rule = services.update_rule(request, rule_id, request.POST)
    if rule is None:
        raise Http404
    return _rules_response(
        request,
        {"toast_variant": "success", "toast_title": "Alert updated", "toast_description": rule["name"]},
    )


@require_POST
def toggle_rule(request, rule_id):
    rule = services.toggle_rule(request, rule_id)
    if rule is None:
        raise Http404
    return _rules_response(
        request,
        {
            "toast_variant": "info",
            "toast_title": "Alert paused" if rule["active"] else "Alert resumed",
            "toast_description": rule["name"],
        },
    )


@require_POST
def duplicate_rule(request, rule_id):
    copy = services.duplicate_rule(request, rule_id)
    if copy is None:
        raise Http404
    return _rules_response(
        request,
        {"toast_variant": "success", "toast_title": "Alert duplicated", "toast_description": copy["name"]},
    )


@require_POST
def delete_rule(request, rule_id):
    name = services.delete_rule(request, rule_id)
    if name is None:
        raise Http404
    return _rules_response(
        request,
        {"toast_variant": "info", "toast_title": "Alert deleted", "toast_description": name},
    )


@require_POST
def open_alert(request, alert_id):
    """Row click: mark the notification read AND open the detail drawer.
    Response: drawer into #drawer-root + OOB recent-alerts fragment + OOB
    sidebar badges."""
    services.mark_read(request, alert_id)
    alert = selectors.alert_by_id(request, alert_id)
    if alert is None:
        raise Http404
    context = {
        **selectors.drawer_context(request, alert),
        **_recent_context(request, request.GET),
    }
    return render(request, "alerts/partials/open_alert_response.html", context)


@require_POST
def mark_read(request, alert_id):
    services.mark_read(request, alert_id)
    return render(
        request,
        "alerts/partials/recent_response.html",
        _recent_context(request, request.GET),
    )


@require_POST
def mark_all_read(request):
    services.mark_all_read(request)
    return render(
        request,
        "alerts/partials/recent_response.html",
        _recent_context(request, request.GET),
    )
