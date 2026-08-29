"""Alerts page, rule dialog, and mutations (rules + notifications)."""
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

from apps.alerts.models import Alert, AlertRule


def _rule_id(workspace, name="Large ToyWorld price drops"):
    return str(AlertRule.objects.get(workspace=workspace, name=name).pk)


def _alert_id(workspace):
    return Alert.objects.filter(workspace=workspace, status="new").first().pk


def test_index_renders(client):
    response = client.get(reverse("alerts:index"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Alert Rules" in content
    assert "Get notified when important competitor activity matches your rules." in content
    assert "Recent Alerts" in content
    assert "Large ToyWorld price drops" in content
    assert "Most Triggered Rules" in content
    assert "Alert Coverage" in content


def test_rules_fragment(client):
    response = client.get(
        reverse("alerts:index"),
        {"status": "active"},
        HTTP_HX_REQUEST="true",
        HTTP_HX_TARGET="alert-rules-fragment",
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert 'id="alert-rules-fragment"' in content
    assert "<h1" not in content


def test_rule_dialog_create(client):
    response = client.get(reverse("alerts:rule_dialog"))
    content = response.content.decode()
    assert response.status_code == 200
    assert "Create alert" in content
    assert "What should trigger the alert?" in content
    assert "Where should this apply?" in content
    assert "Alert me when:" in content
    assert "In RivalTracking" in content
    assert "Email — coming later" in content


def test_rule_dialog_edit(client, workspace):
    response = client.get(reverse("alerts:rule_dialog"), {"rule": _rule_id(workspace)})
    content = response.content.decode()
    assert response.status_code == 200
    assert "Edit alert rule" in content
    assert "Large ToyWorld price drops" in content
    assert "Save changes" in content


def test_index_deep_link_opens_dialog(client):
    response = client.get(
        reverse("alerts:index"),
        {"create": "1", "trigger": "price-decrease", "competitor": "ToyWorld.co.uk"},
    )
    content = response.content.decode()
    assert response.status_code == 200
    # Dialog rendered inline at the end of the page so it auto-opens.
    assert "Create alert" in content
    assert "What should trigger the alert?" in content


def test_create_rule(client):
    response = client.post(
        reverse("alerts:create_rule"),
        {
            "trigger": "price-decrease",
            "operator": "more than",
            "threshold": "15",
            "competitor": "ToyWorld.co.uk",
            "category": "All categories",
            "priority": "high",
            "frequency": "Immediate",
        },
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert 'id="alert-rules-fragment"' in content
    assert "Alert created" in content
    assert "Price decreases — ToyWorld.co.uk" in content
    # Persisted into the store.
    followup = client.get(reverse("alerts:index"))
    assert "Price decreases — ToyWorld.co.uk" in followup.content.decode()


def test_update_rule(client, workspace):
    response = client.post(
        reverse("alerts:update_rule", kwargs={"rule_id": _rule_id(workspace)}),
        {
            "trigger": "price-decrease",
            "operator": "more than",
            "threshold": "25",
            "competitor": "ToyWorld.co.uk",
            "category": "All categories",
            "priority": "high",
            "frequency": "Immediate",
        },
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert "Alert updated" in content
    # Name is preserved on edit.
    assert "Large ToyWorld price drops" in content


def test_update_rule_unknown_404(client):
    response = client.post(
        reverse("alerts:update_rule", kwargs={"rule_id": "nope"}), {}
    )
    assert response.status_code == 404


def test_toggle_rule(client, workspace):
    response = client.post(
        reverse("alerts:toggle_rule", kwargs={"rule_id": _rule_id(workspace)})
    )
    content = response.content.decode()
    assert response.status_code == 200
    # Rule was active, so toggling pauses it.
    assert "Alert paused" in content
    assert "Large ToyWorld price drops" in content


def test_duplicate_rule(client, workspace):
    response = client.post(
        reverse("alerts:duplicate_rule", kwargs={"rule_id": _rule_id(workspace)})
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert "Alert duplicated" in content
    assert "Large ToyWorld price drops (copy)" in content


def test_delete_rule(client, workspace):
    response = client.post(
        reverse("alerts:delete_rule", kwargs={"rule_id": _rule_id(workspace)})
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert "Alert deleted" in content
    assert 'id="alert-rules-fragment"' in content
    # Rule row is gone (recent alerts it triggered are kept, so check the
    # rules fragment in isolation).
    followup = client.get(
        reverse("alerts:index"),
        HTTP_HX_REQUEST="true",
        HTTP_HX_TARGET="alert-rules-fragment",
    )
    assert "Large ToyWorld price drops" not in followup.content.decode()


def test_mark_read_oob_badges(client, workspace):
    response = client.post(
        reverse("alerts:mark_read", kwargs={"alert_id": _alert_id(workspace)})
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert 'id="recent-alerts-fragment"' in content
    # Both sidebar badges OOB-swapped.
    assert 'id="sidebar-alerts-badge"' in content
    assert 'id="sidebar-alerts-badge-mobile"' in content
    assert 'hx-swap-oob="true"' in content


def test_mark_all_read(client):
    response = client.post(reverse("alerts:mark_all_read"))
    content = response.content.decode()
    assert response.status_code == 200
    assert 'id="recent-alerts-fragment"' in content
    assert 'id="sidebar-alerts-badge"' in content
    # Mark-all button is now disabled (no unread left).
    assert "disabled" in content


def test_open_alert_drawer(client, workspace):
    response = client.post(
        reverse("alerts:open_alert", kwargs={"alert_id": _alert_id(workspace)})
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert "Large ToyWorld price drops" in content
    assert "Why you received this alert" in content
    # OOB recent fragment + sidebar badges accompany the drawer.
    assert 'id="recent-alerts-fragment"' in content
    assert 'id="sidebar-alerts-badge"' in content


def test_open_alert_unknown_404(client):
    response = client.post(
        reverse("alerts:open_alert", kwargs={"alert_id": 999999})
    )
    assert response.status_code == 404
