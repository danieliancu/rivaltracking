"""AI provider abstraction, change analysis, tools isolation, conversation persistence."""
import pytest
from django.urls import reverse
from django.utils import timezone

from apps.ai import tools
from apps.ai.models import ChangeAnalysis, Conversation, Message
from apps.ai.providers import get_provider
from apps.ai.providers.stub import StubProvider
from apps.ai.tasks import analyse_change
from apps.changes.models import ChangeEvent
from apps.competitors.models import Competitor

pytestmark = pytest.mark.django_db


def test_default_provider_is_stub(settings):
    settings.AI_PROVIDER = "stub"
    assert isinstance(get_provider(), StubProvider)


def test_stub_analyse_change_price_drop():
    insight = StubProvider().analyse_change(
        {"event_type": "price_decrease", "change_percent": -20.0,
         "product": "Widget", "competitor": "RivalCo", "old_price": "£25", "new_price": "£20"}
    )
    assert "RivalCo" in insight.summary
    assert insight.urgency == "high"
    assert insight.why_it_matters


def _eligible_event(workspace):
    competitor = Competitor.objects.for_workspace(workspace).first()
    return ChangeEvent.objects.create(
        workspace=workspace, competitor=competitor,
        event_type=ChangeEvent.Type.PRICE_DECREASE, kind="drop", label="Price decrease",
        previous_value="£25.00", new_value="£20.00", secondary="-20.0%",
        impact=ChangeEvent.Impact.HIGH, detected_at=timezone.now(),
    )


def test_analyse_change_creates_analysis(workspace):
    event = _eligible_event(workspace)
    result = analyse_change(event.id)
    assert result["analysed"] is True
    analysis = ChangeAnalysis.objects.get(change_event=event)
    assert analysis.summary
    assert analysis.provider == "stub"
    assert analysis.workspace_id == workspace.id


def test_analyse_change_skips_low_significance(workspace):
    competitor = Competitor.objects.for_workspace(workspace).first()
    event = ChangeEvent.objects.create(
        workspace=workspace, competitor=competitor,
        event_type=ChangeEvent.Type.PRODUCT_METADATA_CHANGE, kind="name", label="Name changed",
        impact=ChangeEvent.Impact.LOW, detected_at=timezone.now(),
    )
    assert analyse_change(event.id)["analysed"] is False
    assert not ChangeAnalysis.objects.filter(change_event=event).exists()


def test_tools_are_workspace_scoped(workspace, other_workspace):
    _eligible_event(workspace)  # a distinctive £25.00 → £20.00 drop
    mine = tools.get_recent_changes(workspace, days=30)
    theirs = tools.get_recent_changes(other_workspace, days=30)
    assert any(c["new"] == "£20.00" for c in mine)
    # The other workspace never sees my just-created event.
    assert not any(c["new"] == "£20.00" for c in theirs)


def test_ask_persists_conversation_and_messages(client, workspace):
    response = client.post(reverse("ai:ask"), {"question": "How active is ToyWorld this week?"})
    assert response.status_code == 200
    conv = Conversation.objects.filter(workspace=workspace).order_by("-created_at").first()
    assert conv is not None
    assert Message.objects.filter(conversation=conv, role="user").exists()
    assert Message.objects.filter(conversation=conv, role="ai").exists()


def test_conversations_are_workspace_isolated(client, workspace, other_client, other_workspace):
    client.post(reverse("ai:ask"), {"question": "Secret question about widgets"})
    # The other workspace's Ask AI history never shows my conversation.
    html = other_client.get(reverse("ai:index")).content.decode()
    assert "Secret question about widgets" not in html
