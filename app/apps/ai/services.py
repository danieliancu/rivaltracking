"""Ask AI answering (real workspace data) + conversation persistence.

Ask AI never fabricates business facts: answers are built from the workspace's
own retrieval tools (see build_answer) or an honest no-data response. The
Phase 1 canned-response corpus has been removed from production.
"""
from .models import Conversation, Message


# ---------------------------------------------------------------------------
# Conversation persistence (real Conversation/Message models)


def _workspace(request):
    return getattr(request, "workspace", None)


def _user(request):
    user = getattr(request, "user", None)
    return user if (user is not None and user.is_authenticated) else None


def create_conversation(request, question):
    """Future: POST /api/ai/conversations. Title truncated to 48 chars."""
    title = f"{question[:48]}…" if len(question) > 48 else question
    conversation = Conversation.objects.create(
        workspace=_workspace(request), user=_user(request), title=title
    )
    from .selectors import conversation_dict

    return conversation_dict(conversation)


def record_messages(request, conversation_id, question, response):
    """Persist the user question + AI answer (with citations) for traceability."""
    conv = Conversation.objects.for_workspace(_workspace(request)).filter(
        id=conversation_id
    ).first()
    if conv is None:
        return
    Message.objects.create(conversation=conv, role=Message.Role.USER, content=question)
    Message.objects.create(
        conversation=conv,
        role=Message.Role.AI,
        content=(response or {}).get("summary", ""),
        metadata={"response_id": (response or {}).get("id", "")},
    )
    conv.save(update_fields=["updated_at"])


def rename_conversation(request, conversation_id, title):
    """Future: PATCH /api/ai/conversations/:id"""
    title = (title or "").strip()
    if not title:
        return None
    conv = Conversation.objects.for_workspace(_workspace(request)).filter(
        id=conversation_id
    ).first()
    if conv is None:
        return None
    conv.title = title
    conv.save(update_fields=["title", "updated_at"])
    from .selectors import conversation_dict

    return conversation_dict(conv)


def delete_conversation(request, conversation_id):
    """Future: DELETE /api/ai/conversations/:id"""
    conv = Conversation.objects.for_workspace(_workspace(request)).filter(
        id=conversation_id
    ).first()
    if conv is None:
        return None
    name = conv.title
    conv.delete()
    return name


# ---------------------------------------------------------------------------
# Real, workspace-scoped Ask AI answering (no fabricated business facts)

_GENERIC_FOLLOW_UPS = [
    "What changed this week?",
    "Which of my products are cheapest vs the market?",
    "Any competitor stock-outs right now?",
]


def _scope_prefix(context):
    parts = [
        context.get("competitor"),
        context.get("product"),
        context.get("category"),
        context.get("period"),
        "all competitors" if context.get("scope") == "all-competitors" else None,
    ]
    parts = [p for p in parts if p]
    return ("Scoped to " + " · ".join(parts) + ". ") if parts else ""


def _no_data_answer(data_through):
    return {
        "id": "no-data",
        "heading": "Not enough data collected yet",
        "summary": (
            "I don't have enough data for this workspace yet. Connect your catalogue, "
            "add a competitor and run a scan — then ask me again."
        ),
        "follow_ups": [],
        "data_through": data_through,
        "evidence": [{"label": "Add a competitor", "to": "/competitors/"}],
    }


def _change_bullet(c):
    event = c["event"].replace("_", " ")
    product = f" · {c['product']}" if c["product"] else ""
    return f"**{c['competitor']}** — {event}{product}"


def build_answer(workspace, question, context):
    """Deterministic, real-data Ask AI answer from workspace retrieval tools.

    Never fabricates business facts: it reports what the workspace's own DB
    holds, or an honest no-data response.
    """
    from django.utils import timezone

    from apps.catalogue import selectors as catalogue_selectors
    from apps.catalogue.models import OwnProduct
    from apps.changes.models import ChangeEvent
    from apps.competitors.models import Competitor

    from . import tools

    q = (question or "").lower()
    data_through = timezone.localtime(timezone.now()).strftime("%d %b, %H:%M")
    prefix = _scope_prefix(context or {})

    if not Competitor.objects.for_workspace(workspace).exists() and not ChangeEvent.objects.for_workspace(workspace).exists():
        return _no_data_answer(data_through)

    base = {"id": "answer", "data_through": data_through, "follow_ups": _GENERIC_FOLLOW_UPS, "evidence": []}

    # Price / market position
    if any(w in q for w in ("price", "pricing", "cheap", "expensive", "position", "market", "vs")):
        positions = [
            p for p in catalogue_selectors.workspace_price_positions(workspace)
            if p["our_price"] is not None and p["competitors"]
        ]
        if positions:
            cheaper = sum(1 for p in positions if p["position"] == "cheapest")
            pricier = sum(1 for p in positions if p["position"] == "most_expensive")
            return {**base, "heading": "Your price position",
                    "summary": f"{prefix}{len(positions)} of your products are matched to competitors: "
                               f"{cheaper} are the cheapest and {pricier} are the most expensive.",
                    "metrics": [
                        {"value": str(len(positions)), "label": "Matched products"},
                        {"value": str(cheaper), "label": "Cheapest", "tone": "text-success"},
                        {"value": str(pricier), "label": "Most expensive", "tone": "text-destructive"},
                    ],
                    "bullets": [
                        f"**{p['own_product']}** — ours {p['our_price']} vs lowest {p['lowest']}"
                        for p in positions[:5]
                    ],
                    "next_step": "Connect more of your catalogue to widen the comparison." if len(positions) < 5 else "Review the products where you are the most expensive.",
                    "evidence": [{"label": "View products", "to": "/products/"}]}
        changes = [c for c in tools.get_recent_changes(workspace, days=30, limit=50)
                   if c["event"] in ("price_decrease", "price_increase")]
        return {**base, "heading": "Recent price changes",
                "summary": f"{prefix}{len(changes)} price changes detected in the last 30 days.",
                "bullets": [_change_bullet(c) for c in changes[:6]] or ["No price changes recorded yet."],
                "evidence": [{"label": "View changes", "to": "/changes/?type=price-decrease"}]}

    # Stock
    if any(w in q for w in ("stock", "availability", "out of stock", "sold out")):
        changes = [c for c in tools.get_recent_changes(workspace, days=30, limit=50)
                   if c["event"] in ("stock_out", "stock_in")]
        return {**base, "heading": "Recent stock changes",
                "summary": f"{prefix}{len(changes)} stock changes in the last 30 days.",
                "bullets": [_change_bullet(c) for c in changes[:6]] or ["No stock changes recorded yet."],
                "evidence": [{"label": "View changes", "to": "/changes/?type=out-of-stock"}]}

    # Promotions
    if any(w in q for w in ("promo", "promotion", "discount", "offer")):
        changes = [c for c in tools.get_recent_changes(workspace, days=30, limit=50)
                   if c["event"] in ("promotion_started", "promotion_ended")]
        return {**base, "heading": "Recent promotions",
                "summary": f"{prefix}{len(changes)} promotion changes in the last 30 days.",
                "bullets": [_change_bullet(c) for c in changes[:6]] or ["No promotions detected yet."],
                "evidence": [{"label": "View changes", "to": "/changes/?type=promotion-started"}]}

    # Default: recent activity summary
    recent = tools.get_recent_changes(workspace, days=7, limit=40)
    T = ChangeEvent.Type
    ev = ChangeEvent.objects.for_workspace(workspace).filter(
        detected_at__gte=timezone.now() - timezone.timedelta(days=7)
    )
    return {**base, "heading": "Recent competitor activity",
            "summary": f"{prefix}{len(recent)} changes detected across your competitors in the last 7 days.",
            "metrics": [
                {"value": str(ev.filter(event_type=T.PRICE_DECREASE).count()), "label": "Price drops", "tone": "text-success"},
                {"value": str(ev.filter(event_type=T.PRICE_INCREASE).count()), "label": "Price rises", "tone": "text-destructive"},
                {"value": str(ev.filter(event_type__in=[T.STOCK_IN, T.STOCK_OUT]).count()), "label": "Stock moves"},
                {"value": str(ev.filter(event_type=T.PRODUCT_NEW).count()), "label": "New products"},
            ],
            "bullets": [_change_bullet(c) for c in recent[:6]] or ["No changes in the last 7 days."],
            "next_step": "Ask about a specific competitor, product or category to go deeper.",
            "evidence": [{"label": "View all changes", "to": "/changes/"}]}
