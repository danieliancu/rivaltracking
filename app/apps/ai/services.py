"""Ask AI resolution + conversation mutations against the mock store.

Ports resolveResponse from prototype-react/src/lib/ask-ai-data.ts and the
conversation helpers from workspace-store.tsx (addConversation /
renameConversation / deleteConversation).
"""
import re
from copy import deepcopy
from functools import lru_cache

from apps.core.store import WorkspaceStore

from .data import CANDIDATE_RESPONSE_TEMPLATE, FALLBACK_RESPONSE, RESPONSES


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
# Conversation mutations (workspace-store.tsx)


def _unique_conversation_id(conversations):
    """workspace-store.tsx uses a monotonic counter (`c${n}`); we pick the
    lowest `c{n}` not already taken so ids stay stable and collision-free."""
    existing = {c["id"] for c in conversations}
    n = 1
    while f"c{n}" in existing:
        n += 1
    return f"c{n}"


def create_conversation(request, question):
    """Future: POST /api/ai/conversations

    Mirrors addConversation: title truncated to 48 chars with an ellipsis,
    prepended to the history. `when` is "Just now".
    """
    title = f"{question[:48]}…" if len(question) > 48 else question
    store = WorkspaceStore(request)
    conversation = {
        "id": _unique_conversation_id(store.get("conversations")),
        "title": title,
        "when": "Just now",
    }
    store.mutate("conversations", lambda items: items.insert(0, conversation))
    return conversation


def rename_conversation(request, conversation_id, title):
    """Future: PATCH /api/ai/conversations/:id"""
    title = (title or "").strip()
    if not title:
        return None
    store = WorkspaceStore(request)
    found = {"c": None}

    def _rename(items):
        for c in items:
            if c["id"] == conversation_id:
                c["title"] = title
                found["c"] = c

    store.mutate("conversations", _rename)
    return found["c"]


def delete_conversation(request, conversation_id):
    """Future: DELETE /api/ai/conversations/:id"""
    store = WorkspaceStore(request)
    name = next(
        (c["title"] for c in store.get("conversations") if c["id"] == conversation_id),
        None,
    )
    if name is None:
        return None
    store.replace(
        "conversations",
        [c for c in store.get("conversations") if c["id"] != conversation_id],
    )
    return name
