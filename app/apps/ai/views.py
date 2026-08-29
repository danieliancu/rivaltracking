from urllib.parse import urlencode

from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.competitors import selectors as competitor_selectors
from apps.core.store import WorkspaceStore

from . import selectors, services
from .data import ACTIVITY_SUGGESTIONS, SUGGESTED_QUESTIONS


def _base_context(request):
    return {"conversations": WorkspaceStore(request).get("conversations")}


def index(request):
    context = selectors.parse_context(request, request.GET)
    active_id = (request.GET.get("c") or "").strip() or None
    conversation = (
        selectors.conversation_by_id(request, active_id) if active_id else None
    )

    messages = []
    if conversation:
        messages = selectors.replay_messages(request, conversation)
    active_id = conversation["id"] if conversation else None

    seed_prompt = ""
    if not conversation:
        seed_prompt = (request.GET.get("prompt") or "").replace("-", " ")

    ctx = {
        **_base_context(request),
        "active_id": active_id,
        "messages": messages,
        "started": bool(messages),
        "context": context,
        "context_active": selectors.context_active(context),
        "context_chips": selectors.context_chips(context, active_id),
        "context_query": selectors.context_query(context),
        "seed_prompt": seed_prompt,
        "suggested_questions": SUGGESTED_QUESTIONS,
        "activity_suggestions": ACTIVITY_SUGGESTIONS,
        "competitor_options": [c["name"] for c in competitor_selectors.header_list(request)],
        "period_options": selectors.PERIOD_OPTIONS,
        "category_options": selectors.CATEGORY_OPTIONS,
    }
    return render(request, "ai/index.html", ctx)


def history_sheet(request):
    """Left sheet fragment (HTMX → #drawer-root) — the xl:hidden History button."""
    active_id = (request.GET.get("c") or "").strip() or None
    return render(
        request,
        "ai/partials/history_sheet.html",
        {**_base_context(request), "active_id": active_id},
    )


@require_POST
def ask(request):
    question = (request.POST.get("question") or "").strip()
    context = selectors.parse_context(request, request.POST)
    active_id = (request.POST.get("c") or "").strip() or None
    conversation = (
        selectors.conversation_by_id(request, active_id) if active_id else None
    )

    if question:
        response = services.resolve_response(question, context)
    else:
        response = None

    # First message of a fresh conversation creates the history entry.
    if conversation is None and question:
        conversation = services.create_conversation(request, question)

    ctx = {
        **_base_context(request),
        "active_id": conversation["id"] if conversation else None,
        "question": question,
        "ai_message": selectors.build_ai_message(response) if response else None,
        "context_query": selectors.context_query(context),
    }
    resp = render(request, "ai/partials/thread.html", ctx)

    if conversation:
        params = {"c": conversation["id"], **selectors.context_query(context)}
        resp["HX-Push-Url"] = reverse("ai:index") + "?" + urlencode(params)
    return resp


@require_POST
def rename(request):
    conversation_id = request.POST.get("conversation_id")
    title = request.POST.get("title")
    conversation = services.rename_conversation(request, conversation_id, title)
    active_id = (request.POST.get("c") or "").strip() or None
    ctx = {
        **_base_context(request),
        "active_id": active_id,
        "toast": {
            "variant": "success",
            "title": "Conversation renamed",
            "description": conversation["title"] if conversation else "",
        },
    }
    return render(request, "ai/partials/history_response.html", ctx)


@require_POST
def delete(request):
    conversation_id = request.POST.get("conversation_id")
    active_id = (request.POST.get("c") or "").strip() or None
    name = services.delete_conversation(request, conversation_id)

    # Deleting the active conversation resets to a fresh one (ask-ai.tsx).
    if name is not None and active_id == conversation_id:
        resp = render(request, "ai/partials/history_response.html", {**_base_context(request), "active_id": None})
        resp["HX-Redirect"] = reverse("ai:index")
        return resp

    ctx = {
        **_base_context(request),
        "active_id": active_id,
        "toast": {
            "variant": "info",
            "title": "Conversation deleted",
            "description": name or "",
        },
    }
    return render(request, "ai/partials/history_response.html", ctx)
