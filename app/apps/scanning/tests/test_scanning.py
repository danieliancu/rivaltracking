"""ScanJob creation, dedup, scheduled dispatch and workspace isolation."""
import pytest
from django.urls import reverse
from django.utils import timezone

from apps.competitors.models import Competitor
from apps.scanning import services, tasks
from apps.scanning.models import ScanJob

pytestmark = pytest.mark.django_db


def _competitor(workspace):
    return Competitor.objects.for_workspace(workspace).first()


def test_run_scan_creates_completed_scanjob(client, workspace):
    competitor = _competitor(workspace)
    response = client.post(reverse("competitors:run_scan", args=[competitor.slug]))
    assert response.status_code == 200
    job = ScanJob.objects.filter(competitor=competitor).latest("queued_at")
    # Eager mode runs the job inline to completion.
    assert job.status == ScanJob.Status.COMPLETED
    assert job.trigger_type == ScanJob.Trigger.MANUAL
    assert job.finished_at is not None
    competitor.refresh_from_db()
    assert competitor.last_scan_at is not None
    assert competitor.next_scan_at is not None


def test_enqueue_is_deduped_while_active(workspace):
    competitor = _competitor(workspace)
    # Simulate an already-active job.
    active = ScanJob.objects.create(
        workspace=workspace, competitor=competitor, status=ScanJob.Status.RUNNING
    )
    returned = services.enqueue_scan(competitor)
    assert returned.id == active.id
    assert ScanJob.objects.filter(competitor=competitor).count() == 1


def test_dispatch_due_scans_enqueues_due_competitors(workspace):
    competitor = _competitor(workspace)
    Competitor.objects.filter(id=competitor.id).update(
        monitoring_enabled=True, next_scan_at=timezone.now() - timezone.timedelta(hours=1)
    )
    # Clear any lingering scheduled jobs.
    ScanJob.objects.all().delete()
    result = tasks.dispatch_due_scans()
    assert result["dispatched"] >= 1
    assert ScanJob.objects.filter(
        competitor=competitor, trigger_type=ScanJob.Trigger.SCHEDULED
    ).exists()


def test_scanjob_is_workspace_isolated(workspace, other_workspace):
    mine = _competitor(workspace)
    services.enqueue_scan(mine)
    assert ScanJob.objects.for_workspace(other_workspace).count() == 0
    assert ScanJob.objects.for_workspace(workspace).count() >= 1


def test_execute_scan_job_is_idempotent_on_finished(workspace):
    competitor = _competitor(workspace)
    job = services.create_scan_job(competitor)
    services.execute_scan_job(job.id)
    job.refresh_from_db()
    assert job.status == ScanJob.Status.COMPLETED
    # Running again on a finished job is a no-op.
    assert services.execute_scan_job(job.id) is None


class _BlockedFetcher:
    """Every fetch is refused like a Cloudflare/WAF anti-bot challenge."""

    def fetch(self, url):
        from apps.scanning.scraping.fetchers.base import FetchResult

        return FetchResult(
            url=url,
            status_code=403,
            text="<html><head><title>Just a moment...</title></head></html>",
            final_url=url,
            ok=False,
        )

    def close(self):
        pass


def test_blocked_site_marks_competitor_protected(workspace):
    competitor = _competitor(workspace)
    competitor.status = Competitor.Status.INITIALISING
    competitor.save(update_fields=["status"])
    job = services.create_scan_job(competitor)
    services.execute_scan_job(job.id, fetcher=_BlockedFetcher())
    job.refresh_from_db()
    competitor.refresh_from_db()
    assert job.status == ScanJob.Status.FAILED
    assert competitor.status == Competitor.Status.BLOCKED
    assert "anti-bot" in competitor.note.lower()
