"""Alert evaluation: rule matching, thresholds, delivery and isolation."""
import pytest
from django.core import mail
from django.utils import timezone

from apps.alerts import engine
from apps.alerts.models import Alert, AlertRule
from apps.changes.models import ChangeEvent
from apps.competitors.models import Competitor

pytestmark = pytest.mark.django_db


def _rule(workspace, **overrides):
    defaults = dict(
        workspace=workspace, name="Big drops", type_group="price",
        condition="Price decrease > 10%", competitors="All competitors",
        enabled=True, priority="high", channels=["in_app"],
        config={"trigger_id": "price-decrease", "threshold": "10"},
    )
    defaults.update(overrides)
    return AlertRule.objects.create(**defaults)


def _event(workspace, *, secondary="-20.0%", etype=ChangeEvent.Type.PRICE_DECREASE):
    competitor = Competitor.objects.for_workspace(workspace).first()
    return ChangeEvent.objects.create(
        workspace=workspace, competitor=competitor, event_type=etype,
        kind="drop", label="Price decrease", previous_value="£25.00",
        new_value="£20.00", secondary=secondary, impact="high", detected_at=timezone.now(),
    )


def test_evaluation_creates_alert(workspace):
    _rule(workspace)
    event = _event(workspace)
    created = engine.evaluate_event(event)
    assert len(created) == 1
    assert Alert.objects.filter(workspace=workspace, change_event=event).exists()


def test_threshold_filters_small_changes(workspace):
    _rule(workspace)  # threshold 10%
    event = _event(workspace, secondary="-5.0%")
    assert engine.evaluate_event(event) == []


def test_evaluation_is_idempotent(workspace):
    _rule(workspace)
    event = _event(workspace)
    engine.evaluate_event(event)
    engine.evaluate_event(event)
    assert Alert.objects.filter(change_event=event).count() == 1


def test_email_delivery(workspace, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    _rule(workspace, channels=["in_app", "email"])
    event = _event(workspace)
    engine.evaluate_events([event])
    assert len(mail.outbox) == 1
    assert "Big drops" in mail.outbox[0].subject


def test_evaluation_is_workspace_isolated(workspace, other_workspace):
    _rule(workspace)
    event = _event(other_workspace)  # event belongs to the OTHER workspace
    engine.evaluate_event(event)
    assert Alert.objects.for_workspace(workspace).filter(change_event=event).count() == 0
