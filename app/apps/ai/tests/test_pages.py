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
    assert b"ToyWorld was highly active this week" in response.content  # AI heading


@pytest.mark.parametrize(
    "question,heading",
    [
        ("What changed at ToyWorld this week?", "ToyWorld was highly active this week"),
        ("What should I pay attention to today?", "ToyWorld has the highest activity today"),
        ("Which products had the biggest reductions?", "Largest price reductions this week"),
        ("Compare my competitors", "Competitor comparison — this week"),
        # "price activity" + "toyworld" hits the earlier toyworld-week pattern first
        # (faithful first-match); a neutral phrasing reaches the chart response.
        ("Show me the price activity trend", "ToyWorld price activity — last 30 days"),
        ("What new products have appeared recently?", "117 new products appeared this month"),
        ("Where are competitors having stock problems?", "Stock problems concentrate at HappyToyHouse"),
        ("Find potential gaps in competitor catalogues.", "Potential catalogue opportunities"),
        # fallback heading ("Today's ...") — apostrophe is HTML-escaped, match the tail.
        ("Tell me something random", "competitor activity at a glance"),
    ],
)
def test_ask_returns_canned_response(client, question, heading):
    response = client.post(reverse("ai:ask"), {"question": question})
    assert response.status_code == 200
    assert heading.encode() in response.content
    # A fresh conversation was created and pushed.
    assert "HX-Push-Url" in response


def test_ask_with_context_prefixes_scope(client):
    response = client.post(
        reverse("ai:ask"),
        {"question": "Compare my competitors", "competitor": "ToyWorld.co.uk", "category": "Outdoor Toys"},
    )
    assert response.status_code == 200
    assert b"Scoped to ToyWorld.co.uk" in response.content
    assert b"Outdoor Toys" in response.content


def test_ask_candidate_short_circuits(client):
    response = client.post(
        reverse("ai:ask"),
        {"question": "Tell me about them", "competitor": "BrightSpark Toys", "candidate": "1"},
    )
    assert response.status_code == 200
    assert b"BrightSpark Toys is not monitored yet" in response.content


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
