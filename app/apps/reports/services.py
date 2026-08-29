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
    sections = build_report_sections(ws, report.period)
    report.config = {
        **(report.config or {}),
        "metrics": compute_metrics(ws, report.period),
        "data_through": timezone.localtime(now).strftime("%d %b, %H:%M"),
        "sections": sections,
    }
    report.summary = sections["executive_summary"] if report.config.get("ai_analysis", True) else ""
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


def build_report_sections(workspace, period):
    """Full report body computed from real ORM data (+ deterministic narrative).

    Same shape the detail template consumes, but every number traces to this
    workspace's ChangeEvents/competitors — a fresh workspace yields empty
    sections, never fabricated market data.
    """
    from django.db.models import Count
    from django.db.models.functions import TruncDate

    from apps.ai.providers import get_provider
    from apps.changes.models import ChangeEvent
    from apps.competitors.models import Competitor

    T = ChangeEvent.Type
    now = timezone.now()
    since = now - timedelta(days=PERIOD_DAYS.get(period, 7))
    ev = ChangeEvent.objects.for_workspace(workspace).filter(detected_at__gte=since)
    m = compute_metrics(workspace, period)

    metrics = [
        {"id": "changes", "label": "Changes", "value": str(m["total_changes"]), "tone": "info"},
        {"id": "new", "label": "New products", "value": str(m["new_products"]), "tone": "success"},
        {"id": "drops", "label": "Price drops", "value": str(m["price_decreases"]), "tone": "success"},
        {"id": "increases", "label": "Price increases", "value": str(m["price_increases"]), "tone": "danger"},
        {"id": "stockouts", "label": "Stock-outs", "value": str(m["stock_outs"]), "tone": "warning"},
        {"id": "promos", "label": "Promotions", "value": str(m["promotions"]), "tone": "purple"},
    ]

    comparison = []
    for c in Competitor.objects.for_workspace(workspace):
        cev = ev.filter(competitor=c)
        comparison.append({
            "name": c.name, "products": c.products_count or 0,
            "new_products": cev.filter(event_type=T.PRODUCT_NEW).count(),
            "drops": cev.filter(event_type=T.PRICE_DECREASE).count(),
            "increases": cev.filter(event_type=T.PRICE_INCREASE).count(),
            "stockouts": cev.filter(event_type=T.STOCK_OUT).count(),
            "promos": cev.filter(event_type=T.PROMOTION_STARTED).count(),
            "total": cev.count(),
        })
    comparison.sort(key=lambda r: -r["total"])

    def _by_day(qs):
        return {r["d"]: r["n"] for r in qs.annotate(d=TruncDate("detected_at")).values("d").annotate(n=Count("id"))}

    dec_by_day = _by_day(ev.filter(event_type=T.PRICE_DECREASE))
    inc_by_day = _by_day(ev.filter(event_type=T.PRICE_INCREASE))
    days = sorted(set(dec_by_day) | set(inc_by_day))
    pricing = {
        "facts": [
            {"label": "Price decreases", "value": str(m["price_decreases"]), "tone": "text-success"},
            {"label": "Price increases", "value": str(m["price_increases"]), "tone": "text-destructive"},
        ],
        "series": [{"day": f"{d:%d %b}", "decreases": dec_by_day.get(d, 0), "increases": inc_by_day.get(d, 0)} for d in days],
        "ai_note": "",
    }

    cats = (
        ev.exclude(product__isnull=True).exclude(product__category="")
        .values("product__category").annotate(n=Count("id")).order_by("-n")[:6]
    )
    category_comparison = [{"name": r["product__category"], "changes": r["n"]} for r in cats]

    stock_facts = {
        "title": "Stock Intelligence",
        "facts": [
            {"label": "Stock-outs", "value": str(m["stock_outs"])},
            {"label": "Back in stock", "value": str(ev.filter(event_type=T.STOCK_IN).count())},
        ],
        "ai_note": "",
    }
    promo_facts = {
        "title": "Promotion Intelligence",
        "facts": [
            {"label": "Newly detected", "value": str(m["promotions"])},
            {"label": "Ended", "value": str(ev.filter(event_type=T.PROMOTION_ENDED).count())},
        ],
        "ai_note": "",
    }
    catalogue_facts = {
        "title": "Catalogue Intelligence",
        "facts": [
            {"label": "New products", "value": str(m["new_products"])},
            {"label": "Removed products", "value": str(ev.filter(event_type=T.PRODUCT_REMOVED).count())},
        ],
        "ai_note": "",
    }

    developments = []
    for i, row in enumerate(comparison[:3], start=1):
        if row["total"] < 1:
            continue
        developments.append({
            "rank": i,
            "title": f"{row['name']} led activity",
            "facts": [f"{row['total']} changes", f"{row['drops']} price drops", f"{row['stockouts']} stock-outs"],
            "evidence": {"label": f"View {row['total']} changes", "to": f"/changes?range=7d"},
            "tone": "bg-info/10 text-info",
        })

    risks, opportunities, actions = [], [], []
    if comparison and comparison[0]["drops"]:
        top = comparison[0]
        risks.append(f"{top['name']} is applying pricing pressure with {top['drops']} price reductions in the period.")
        actions.append("Review your pricing on the affected products and decide whether to respond.")
    if m["stock_outs"]:
        opportunities.append(f"Competitors recorded {m['stock_outs']} stock-outs — an opportunity to capture demand while they cannot fulfil it.")

    provider = get_provider()
    exec_summary = provider.generate_report_summary(
        workspace, {"total_changes": m["total_changes"], "competitors": len(comparison)}
    )
    key_takeaway = (
        f"{m['total_changes']} tracked changes across {len(comparison)} competitors this period."
        if m["total_changes"] else
        "Not enough data collected yet for this period — connect competitors and run scans."
    )

    return {
        "metrics": metrics,
        "competitor_comparison": comparison,
        "pricing": pricing,
        "category_comparison": category_comparison,
        "stock": stock_facts,
        "promotions": promo_facts,
        "catalogue": catalogue_facts,
        "developments": developments,
        "opportunities": opportunities,
        "risks": risks,
        "recommended_actions": actions,
        "executive_summary": exec_summary,
        "key_takeaway": key_takeaway,
    }
