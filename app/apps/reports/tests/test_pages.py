import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_index_renders_full_shell(client):
    resp = client.get(reverse("reports:index"))
    assert resp.status_code == 200
    body = resp.content.decode()
    assert "Report Library" in body
    assert "Generated Reports" in body
    assert "Scheduled Reports" in body


def test_detail_ready_report(client):
    resp = client.get(reverse("reports:detail", args=["weekly-week-34"]))
    assert resp.status_code == 200
    body = resp.content.decode()
    assert "Weekly Intelligence — Week 34" in body
    assert "Executive Summary" in body
    assert "Competitor Comparison" in body


def test_detail_missing_report(client):
    resp = client.get(reverse("reports:detail", args=["nope"]))
    assert resp.status_code == 200
    assert "Report not found" in resp.content.decode()


def test_create_dialog_fragment(client):
    resp = client.get(reverse("reports:create_dialog"))
    assert resp.status_code == 200
    assert "Create report" in resp.content.decode()


def test_create_dialog_fragment_with_type(client):
    resp = client.get(reverse("reports:create_dialog") + "?type=pricing")
    assert resp.status_code == 200


def test_schedule_dialog_fragment(client):
    resp = client.get(reverse("reports:schedule_dialog"))
    assert resp.status_code == 200
    assert "Schedule report" in resp.content.decode()


def test_export_csv(client):
    resp = client.get(reverse("reports:export_csv", args=["weekly-week-34"]))
    assert resp.status_code == 200
    assert resp["Content-Type"].startswith("text/csv")
    assert "Weekly Intelligence — Week 34" in resp.content.decode()


def test_create_report_post(client):
    resp = client.post(
        reverse("reports:create"),
        {"type_id": "weekly", "competitors": "All monitored competitors", "date_range": "Last 7 days"},
    )
    assert resp.status_code == 200
    body = resp.content.decode()
    assert "Report ready" in body
    assert "Preparing report" in body


def test_delete_report_post(client):
    resp = client.post(reverse("reports:delete", args=["weekly-week-34"]))
    assert resp.status_code == 200
    body = resp.content.decode()
    # Toast confirms the deletion (its description echoes the report name).
    assert "Report deleted" in body


def test_save_schedule_post(client):
    resp = client.post(
        reverse("reports:save_schedule"),
        {"type_id": "daily", "competitors": "All monitored competitors", "frequency": "Daily", "time": "08:00"},
    )
    assert resp.status_code == 200
    assert "Report scheduled" in resp.content.decode()
