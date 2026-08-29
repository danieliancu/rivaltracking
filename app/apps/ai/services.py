"""Ask AI resolution + conversation mutations against the mock store.

Ports resolveResponse from prototype-react/src/lib/ask-ai-data.ts and the
conversation helpers from workspace-store.tsx (addConversation /
renameConversation / deleteConversation).
"""
import re
from copy import deepcopy
from functools import lru_cache

from .data import CANDIDATE_RESPONSE_TEMPLATE, FALLBACK_RESPONSE, RESPONSES
from .models import Conversation, Message


@lru_cache(maxsize=1)
def _compiled_responses():
    """RESPONSES with their pattern strings compiled (re.IGNORECASE), matched
    in declaration order — the first hit wins, exactly like resolveResponse."""
    return [(re.compile(r["pattern"], re.IGNORECASE), r["response"]) for r in RESPONSES]


def _candidate_response(name):
    """Format CANDIDATE_RESPONSE_TEMPLATE for an unmonitored discovery
    candidate (ask-ai-data.ts candidateResponse)."""
    response = deepcopy(CANDIDATE_RESPONSE_TEMPLATE)
    for key in ("id", "heading", "summary", "next_step"):
        if key in response and "{name}" in response[key]:
            response[key] = response[key].format(name=name)
    return response


def resolve_response(question, context=None):
    """Future: POST /api/ai/query

    Faithful port of resolveResponse:
    - candidate short-circuit (context.candidate AND context.competitor);
    - else first RESPONSES regex match (case-insensitive) over the question;
    - else FALLBACK_RESPONSE;
    - then, if any scope parts are set, prefix the summary with
      "Scoped to {parts}. " (parts joined with " · ").

    Returns a deep copy so the prefix never mutates the seed data.
    """
    context = context or {}

    if context.get("candidate") and context.get("competitor"):
        return _candidate_response(context["competitor"])

    base = None
    for pattern, response in _compiled_responses():
        if pattern.search(question):
            base = response
            break
    if base is None:
        base = FALLBACK_RESPONSE
    result = deepcopy(base)

    scope_parts = [
        context.get("competitor"),
        context.get("product"),
        context.get("category"),
        context.get("period"),
        "All competitors" if context.get("scope") == "all-competitors" else None,
    ]
    scope_parts = [p for p in scope_parts if p]
    if scope_parts:
        prefix = "Scoped to " + " · ".join(scope_parts) + ". "
        result["summary"] = (prefix + (result.get("summary") or "")).strip()
    return result


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
