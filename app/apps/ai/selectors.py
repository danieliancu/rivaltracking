"""Ask AI reads: context parsing, conversation replay and chart payloads.

Context handed to the AI service alongside the question (ask-ai.tsx). It lives
in the URL query string here so the page is shareable/reloadable:
    ?competitor=&period=&category=&product=&scope=&candidate=&prompt=&c=
Deep links from other pages arrive with slug/token values (competitor slug,
product slug, category token, range key) which are resolved to display names;
the context-bar form round-trips the display names it already produced.
"""
from uuid import uuid4

from apps.competitors import selectors as competitors
from apps.core.entities import category_from_param
from apps.products.data import FILTER_OPTIONS

from . import services

# ai-context-bar.tsx select options.
PERIOD_OPTIONS = ["Today", "Last 7 days", "Last 30 days", "Custom"]
CATEGORY_OPTIONS = [
    "Outdoor Toys",
    "Educational Toys",
    "Construction Toys",
    "Baby Toys",
    "Plush Toys",
    "Personalised Toys",
]

# ask-ai.tsx rangePeriods: deep-link ?range= tokens → period display names.
RANGE_PERIODS = {"today": "Today", "7d": "Last 7 days", "30d": "Last 30 days"}


def _product_name(request, value):
    from apps.products import selectors as products

    for row in products.all_rows(request):
        if row["slug"] == value:
            return row["name"]
    return value


def parse_context(request, params):
    """Build the display-name context dict from query/POST params. Accepts both
    slug/token values (deep links) and display names (context-bar round-trip)."""
    context = {}

    competitor = (params.get("competitor") or "").strip()
    if competitor:
        context["competitor"] = competitors.name_for(request, competitor) or competitor

    period = (params.get("period") or "").strip()
    if not period:
        range_token = (params.get("range") or "").strip().lower()
        if range_token in RANGE_PERIODS:
            period = RANGE_PERIODS[range_token]
    if period:
        context["period"] = period

    category = (params.get("category") or "").strip()
    if category:
        context["category"] = (
            category_from_param(category, CATEGORY_OPTIONS) or category
        )

    product = (params.get("product") or "").strip()
    if product:
        context["product"] = _product_name(request, product)

    scope = (params.get("scope") or "").strip()
    if scope:
        context["scope"] = scope

    if str(params.get("candidate") or "").lower() in ("1", "true", "yes"):
        context["candidate"] = True

    return context


def context_active(context):
    """Whether any user-visible scope chip should show (ai-context-bar.tsx)."""
    return any(context.get(k) for k in ("competitor", "period", "category", "product", "scope"))


def context_query(context):
    """The context as URL params (display values), for links / push-url."""
    params = {}
    for key in ("competitor", "period", "category", "product", "scope"):
        if context.get(key):
            params[key] = context[key]
    if context.get("candidate"):
        params["candidate"] = "1"
    return params


def context_chips(context, active_id=None):
    """Removable chips in ai-context-bar.tsx order: competitor, period,
    category, product, scope. Each carries a removal link that drops just that
    param (keeping the active conversation)."""
    from urllib.parse import urlencode

    order = [
        ("competitor", context.get("competitor")),
        ("period", context.get("period")),
        ("category", context.get("category")),
        ("product", context.get("product")),
        ("scope", "All competitors" if context.get("scope") == "all-competitors" else None),
    ]
    base = context_query(context)
    chips = []
    for key, value in order:
        if not value:
            continue
        remaining = {k: v for k, v in base.items() if k != key}
        if active_id:
            remaining = {"c": active_id, **remaining}
        query = urlencode(remaining)
        chips.append({"key": key, "value": value, "remove_url": "?" + query if query else "?"})
    return chips


# ---------------------------------------------------------------------------
# Responses + chart payloads


def _chart_payload(chart):
    """AIResponse bar chart (ai-response.tsx): vertical bars, barSize 38,
    chart-1 fill."""
    return {
        "type": "bar",
        "labels": [p["label"] for p in chart["series"]],
        "series": [{"data": [p["value"] for p in chart["series"]], "color": "chart-1"}],
        "options": {"barSize": 38},
    }


# ai-response.tsx actionMeta: icon + default destination per action kind.
ACTION_META = {
    "alert": {"icon": "bell", "to": "/alerts"},
    "report": {"icon": "file-bar-chart-2", "to": "/reports"},
    "changes": {"icon": "git-compare-arrows", "to": "/changes"},
    "products": {"icon": "package", "to": "/products"},
}


def _action_href(action):
    """The create-dialog deep links / filtered destinations from ai-response.tsx
    act(): alert → /alerts?create=1&…, report → /reports?create=<id>, else a.to."""
    kind = action.get("kind")
    if kind == "alert":
        params = {"create": "1"}
        prefill = action.get("alert_prefill") or {}
        if prefill.get("kind"):
            params["trigger"] = prefill["kind"]
        if prefill.get("competitor"):
            params["competitor"] = prefill["competitor"]
        if prefill.get("category"):
            params["category"] = prefill["category"]
        from urllib.parse import urlencode

        return "/alerts?" + urlencode(params)
    if kind == "report":
        type_id = action.get("report_type_id")
        return f"/reports?create={type_id}" if type_id else "/reports?create=1"
    return action.get("to") or ACTION_META.get(kind, {}).get("to", "#")


def build_ai_message(response):
    """Wrap a resolved response with a unique chart id + payload and resolved
    action icons/hrefs for the card."""
    message = {"role": "ai", "response": response, "chart_payload": None, "chart_id": None}
    if response.get("chart"):
        message["chart_id"] = f"ai-chart-{uuid4().hex[:8]}"
        message["chart_payload"] = _chart_payload(response["chart"])
    message["actions"] = [
        {
            **action,
            "icon": ACTION_META.get(action.get("kind"), {}).get("icon", "arrow-right"),
            "href": _action_href(action),
        }
        for action in response.get("actions", [])
    ]
    return message


def conversation_dict(obj):
    from apps.core.format import relative_time
    from django.utils import timezone

    minutes = max(0, int((timezone.now() - obj.updated_at).total_seconds() // 60))
    return {"id": str(obj.pk), "title": obj.title, "when": relative_time(minutes)}


def list_conversations(request):
    from .models import Conversation

    return [
        conversation_dict(c)
        for c in Conversation.objects.for_workspace(getattr(request, "workspace", None))
    ]


def conversation_by_id(request, conversation_id):
    from .models import Conversation

    obj = (
        Conversation.objects.for_workspace(getattr(request, "workspace", None))
        .filter(pk=conversation_id)
        .first()
    )
    return conversation_dict(obj) if obj else None


def replay_messages(request, conversation):
    """Opening a stored conversation replays its topic as a fresh answer
    (ask-ai.tsx onOpen): [user: title, ai: resolveResponse(title)] — no
    context is applied to the replay."""
    from apps.ai.providers import get_provider

    response = get_provider().answer_question(
        getattr(request, "workspace", None), conversation["title"], {}
    )
    return [
        {"role": "user", "text": conversation["title"]},
        build_ai_message(response),
    ]
