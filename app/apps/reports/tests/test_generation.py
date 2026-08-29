"""Report generation from real ORM data + schedules."""
import pytest

from apps.reports import services
from apps.reports.models import Report, ReportSchedule

pytestmark = pytest.mark.django_db


class _Req:
    def __init__(self, workspace, user):
        self.workspace = workspace
        self.user = user


def test_create_report_generates_real_metrics(workspace, owner_user):
    req = _Req(workspace, owner_user)
    result = services.create_report(
        req, type_id="weekly", type_title="Weekly Intelligence",
        competitors="All", period="Last 30 days",
    )
    report = Report.objects.get(pk=int(result["id"]))
    assert report.status == Report.Status.READY
    assert report.generated_at is not None
    metrics = report.config["metrics"]
    # Seeded change events exist, so the deterministic totals are populated.
    assert metrics["total_changes"] >= 1
    assert report.summary  # AI narrative (stub) present


def test_report_is_workspace_isolated(workspace, other_workspace, owner_user):
    req = _Req(workspace, owner_user)
    result = services.create_report(req, type_id="weekly", type_title="Zzq Unique", competitors="All", period="Last 7 days")
    assert Report.objects.for_workspace(workspace).filter(pk=int(result["id"])).exists()
    assert not Report.objects.for_workspace(other_workspace).filter(pk=int(result["id"])).exists()


def test_save_and_toggle_schedule(workspace, owner_user):
    req = _Req(workspace, owner_user)
    saved = services.save_schedule(req, {
        "id": services.new_schedule_id("daily"), "name": "Daily", "type_id": "daily",
        "competitors": "All competitors", "frequency": "Every day", "time": "08:00", "active": True,
    })
    obj = ReportSchedule.objects.get(pk=int(saved["id"]))
    assert obj.enabled is True
    services.toggle_schedule(req, saved["id"])
    obj.refresh_from_db()
    assert obj.enabled is False
