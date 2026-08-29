"""Report generation + schedule mutations over the Report/ReportSchedule models.

Numeric sections are deterministic (computed from ChangeEvent over the period);
only the narrative summary uses AI.
"""
import time
from datetime import timedelta

from django.utils import timezone

from apps.changes.models import ChangeEvent
from apps.competitors.models import Competitor

from .models import Report, ReportSchedule

PERIOD_DAYS = {"Today": 1, "Last 7 days": 7, "Last 30 days": 30, "Last 24 hours": 1}


def _workspace(request):
    return getattr(request, "workspace", None)


def _user(request):
    user = getattr(request, "user", None)
    return user if (user is not None and user.is_authenticated) else None


def _pk(value):
    return int(value) if str(value).isdigit() else None


def _base36(value):
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    while value:
        value, rem = divmod(value, 36)
        out = digits[rem] + out
    return out or "0"


def compute_metrics(workspace, period):
    """Deterministic report metrics from ChangeEvent over the period window."""
    now = timezone.now()
    since = now - timedelta(days=PERIOD_DAYS.get(period, 7))
    events = ChangeEvent.objects.for_workspace(workspace).filter(detected_at__gte=since)
    T = ChangeEvent.Type
    return {
        "total_changes": events.count(),
        "new_products": events.filter(event_type=T.PRODUCT_NEW).count(),
        "price_decreases": events.filter(event_type=T.PRICE_DECREASE).count(),
        "price_increases": events.filter(event_type=T.PRICE_INCREASE).count(),
        "stock_outs": events.filter(event_type=T.STOCK_OUT).count(),
        "promotions": events.filter(event_type=T.PROMOTION_STARTED).count(),
    }


def generate(report):
    """Populate a report from real data (+ AI narrative); mark it ready."""
    from apps.ai.providers import get_provider

    ws = report.workspace
    now = timezone.now()
    metrics = compute_metrics(ws, report.period)
    report.config = {
        **(report.config or {}),
        "metrics": metrics,
        "data_through": timezone.localtime(now).strftime("%d %b, %H:%M"),
    }
    if report.config.get("ai_analysis", True):
        report.summary = get_provider().generate_report_summary(
            ws,
            {"total_changes": metrics["total_changes"],
             "competitors": Competitor.objects.for_workspace(ws).count()},
        )
    report.status = Report.Status.READY
    report.generated_at = now
    report.save()
    return report


def create_report(request, *, type_id, type_title, competitors, period,
                  category=None, change_type=None, ai_analysis=True):
    """Future: POST /api/reports → generate a Report from real data."""
    report = Report.objects.create(
        workspace=_workspace(request),
        generated_by=_user(request),
        title=f"{type_title} — {period}",
        report_type=type_id,
        competitors=competitors,
        period=period,
        status=Report.Status.GENERATING,
        config={
            "type_title": type_title,
            "category": category,
            "change_type": change_type,
            "ai_analysis": ai_analysis,
        },
    )
    generate(report)
    from .selectors import report_dict

    return report_dict(report)


def delete_report(request, report_id):
    """Future: DELETE /api/reports/:id"""
    Report.objects.for_workspace(_workspace(request)).filter(pk=_pk(report_id)).delete()


def new_schedule_id(type_id):
    """Placeholder id for a not-yet-saved schedule (real id is the pk once saved)."""
    return f"s-{type_id}-{_base36(int(time.time() * 1000))}"


def save_schedule(request, schedule):
    """Future: POST/PATCH /api/report-schedules — create or update by pk."""
    ws = _workspace(request)
    sid = _pk(schedule.get("id"))
    obj = ReportSchedule.objects.for_workspace(ws).filter(pk=sid).first() if sid else None
    fields = {
        "name": schedule["name"],
        "report_type": schedule["type_id"],
        "competitors": schedule["competitors"],
        "frequency": schedule["frequency"],
        "run_time": schedule["time"],
        "enabled": schedule.get("active", True),
    }
    if obj is None:
        obj = ReportSchedule.objects.create(workspace=ws, **fields)
    else:
        for key, value in fields.items():
            setattr(obj, key, value)
        obj.save()
    from .selectors import schedule_dict

    return schedule_dict(obj)


def toggle_schedule(request, schedule_id):
    """Future: PATCH /api/report-schedules/:id (pause/resume)"""
    obj = ReportSchedule.objects.for_workspace(_workspace(request)).filter(
        pk=_pk(schedule_id)
    ).first()
    if obj is None:
        return None
    obj.enabled = not obj.enabled
    obj.save(update_fields=["enabled"])
    from .selectors import schedule_dict

    return schedule_dict(obj)


def delete_schedule(request, schedule_id):
    """Future: DELETE /api/report-schedules/:id"""
    ReportSchedule.objects.for_workspace(_workspace(request)).filter(
        pk=_pk(schedule_id)
    ).delete()
