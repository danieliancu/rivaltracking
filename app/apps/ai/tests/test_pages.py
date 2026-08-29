import pytest

from apps.ai.models import Conversation
from django.urls import reverse

pytestmark = pytest.mark.django_db


def _conv_id(workspace, title):
    return str(Conversation.objects.get(workspace=workspace, title=title).pk)


def test_index_renders_empty_state(client):
    response = client.get(reverse("ai:index"))
    assert response.status_code == 200
    assert b"What would you like to know?" in response.content
    assert b"Powered by your RivalTracking data" in response.content


def test_index_replays_stored_conversation(client, workspace):
    # Seeded "ToyWorld weekly activity" conversation replays a resolved answer.
    response = client.get(reverse("ai:index"), {"c": _conv_id(workspace, "ToyWorld weekly activity")})
    assert response.status_code == 200
    assert b"ToyWorld weekly activity" in response.content  # user bubble (title)
    # Replays a real, data-derived answer (not a canned business fact).
    assert b"Recent competitor activity" in response.content


@pytest.mark.parametrize(
    "question,heading",
    [
        ("What changed this week?", "Recent competitor activity"),
        ("Which products are cheapest vs the market?", "Your price position"),
        ("Where are competitors out of stock?", "Recent stock changes"),
        ("Any promotions running?", "Recent promotions"),
    ],
)
def test_ask_returns_real_answer(client, question, heading):
    response = client.post(reverse("ai:ask"), {"question": question})
    assert response.status_code == 200
    assert heading.encode() in response.content
    assert "HX-Push-Url" in response
    # No fabricated Phase 1 business facts leak into answers.
    assert b"was highly active this week" not in response.content


def test_ask_with_context_prefixes_scope(client):
    response = client.post(
        reverse("ai:ask"),
        {"question": "Compare my competitors", "competitor": "ToyWorld.co.uk", "category": "Outdoor Toys"},
    )
    assert response.status_code == 200
    assert b"Scoped to ToyWorld.co.uk" in response.content
    assert b"Outdoor Toys" in response.content


def test_ask_renders_answer_card(client):
    response = client.post(
        reverse("ai:ask"),
        {"question": "What changed recently?"},
    )
    assert response.status_code == 200
    assert b"Recent competitor activity" in response.content


def test_rename_conversation(client, workspace):
    response = client.post(
        reverse("ai:rename"),
        {"conversation_id": _conv_id(workspace, "Outdoor Toys pricing"), "title": "Renamed topic"},
    )
    assert response.status_code == 200
    assert b"Renamed topic" in response.content
    # Persisted for the next read.
    follow = client.get(reverse("ai:index"))
    assert b"Renamed topic" in follow.content


def test_delete_conversation(client, workspace):
    response = client.post(
        reverse("ai:delete"),
        {"conversation_id": _conv_id(workspace, "Compare ToyWorld vs PlayNest")},
    )
    assert response.status_code == 200
    follow = client.get(reverse("ai:index"))
    assert b"Compare ToyWorld vs PlayNest" not in follow.content


def test_delete_active_conversation_redirects(client, workspace):
    cid = _conv_id(workspace, "ToyWorld weekly activity")
    response = client.post(
        reverse("ai:delete"), {"conversation_id": cid, "c": cid}
    )
    assert response.status_code == 200
    assert response["HX-Redirect"] == reverse("ai:index")


def test_index_seeds_prompt(client):
    response = client.get(reverse("ai:index"), {"prompt": "compare-my-competitors"})
    assert response.status_code == 200
    assert b"compare my competitors" in response.content  # dashes -> spaces, in composer


def test_history_sheet_fragment(client):
    response = client.get(reverse("ai:history_sheet"))
    assert response.status_code == 200
    assert b"Conversations" in response.content
    assert b"ai-history-sheet" in response.content
