"""Read helpers for scan status and health."""
from django.db.models import Count
from django.utils import timezone

from apps.core.format import relative_time

from .models import ScanJob


def _minutes_since(dt, now):
    if dt is None:
        return None
    return max(0, int((now - dt).total_seconds() // 60))


def latest_job_for(request, competitor):
    return (
        ScanJob.objects.for_workspace(getattr(request, "workspace", None))
        .filter(competitor=competitor)
        .order_by("-queued_at")
        .first()
    )


def recent_jobs(request, limit=20):
    now = timezone.now()
    jobs = (
        ScanJob.objects.for_workspace(getattr(request, "workspace", None))
        .select_related("competitor")
        .order_by("-queued_at")[:limit]
    )
    return [
        {
            "id": j.id,
            "competitor": j.competitor.name,
            "status": j.status,
            "trigger": j.trigger_type,
            "changes_detected": j.changes_detected,
            "products_updated": j.products_updated,
            "pages_requested": j.pages_requested,
            "errors_count": j.errors_count,
            "when": relative_time(_minutes_since(j.queued_at, now)),
            "duration": j.duration_seconds,
        }
        for j in jobs
    ]


def scan_health(request):
    """Aggregate scan health for the Overview scan-health card."""
    qs = ScanJob.objects.for_workspace(getattr(request, "workspace", None))
    by_status = {
        row["status"]: row["n"] for row in qs.values("status").annotate(n=Count("id"))
    }
    total = sum(by_status.values())
    completed = by_status.get(ScanJob.Status.COMPLETED, 0)
    failed = by_status.get(ScanJob.Status.FAILED, 0) + by_status.get(
        ScanJob.Status.PARTIALLY_FAILED, 0
    )
    return {
        "total": total,
        "completed": completed,
        "failed": failed,
        "running": by_status.get(ScanJob.Status.RUNNING, 0)
        + by_status.get(ScanJob.Status.QUEUED, 0),
        "success_rate": round(completed / total * 100) if total else 100,
    }
