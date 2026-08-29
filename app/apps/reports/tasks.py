"""Report generation + schedule dispatch on the `reports` queue."""
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from . import services
from .models import Report, ReportSchedule

_FREQ_DAYS = {"Every day": 1, "Every Monday": 7, "Every week": 7, "Every month": 30}


@shared_task(queue="reports")
def generate_report(report_id):
    report = Report.objects.filter(id=report_id).first()
    if report is None:
        return {"generated": False}
    services.generate(report)
    return {"generated": True, "report_id": report_id}


@shared_task(queue="reports")
def dispatch_due_schedules():
    now = timezone.now()
    due = ReportSchedule.objects.filter(enabled=True, next_run_at__lte=now)
    count = 0
    for schedule in due.iterator():
        report = Report.objects.create(
            workspace=schedule.workspace,
            title=f"{schedule.name} — {now:%d %b}",
            report_type=schedule.report_type,
            competitors=schedule.competitors,
            period="Last 7 days",
            status=Report.Status.GENERATING,
            config={"type_title": schedule.name, "ai_analysis": True},
        )
        services.generate(report)
        schedule.next_run_at = now + timedelta(days=_FREQ_DAYS.get(schedule.frequency, 1))
        schedule.save(update_fields=["next_run_at"])
        count += 1
    return {"dispatched": count}
