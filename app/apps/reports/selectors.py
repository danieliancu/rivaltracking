"""Report reads: store lookups, form option shaping, detail chart payloads."""
from urllib.parse import urlencode

from django.urls import reverse
from django.utils import timezone

from apps.core.format import relative_time

from .models import Report, ReportSchedule
from .data import (
    GENERATION_STAGES,
    REPORT_FORM_OPTIONS,
    REPORT_TYPES,
)

# reports.tsx kpiIcons — id → lucide glyph.
KPI_ICONS = {
    "generated": "file-bar-chart-2",
    "scheduled": "calendar-clock",
    "covered": "users",
    "latest": "badge-check",
}

# report-details.tsx metricIcons — id → lucide glyph.
METRIC_ICONS = {
    "changes": "git-compare-arrows",
    "new": "sparkles",
    "drops": "trending-down",
    "increases": "trending-up",
    "stockouts": "package-x",
    "promos": "badge-percent",
}

# schedule-report-dialog.tsx frequencyLabels.
FREQUENCY_LABELS = {
    "Daily": "Every day",
    "Weekly": "Every Monday",
    "Monthly": "Every month",
}


def kpi_cards(request):
    from apps.competitors import selectors as competitor_selectors

    ws = _workspace(request)
    reports = Report.objects.for_workspace(ws)
    latest = reports.exclude(generated_at=None).order_by("-generated_at").first()
    latest_val = "—"
    if latest and latest.generated_at:
        mins = max(0, int((timezone.now() - latest.generated_at).total_seconds() // 60))
        latest_val = relative_time(mins)
    values = [
        ("generated", "Reports generated", str(reports.count()), "info"),
        ("scheduled", "Scheduled reports", str(ReportSchedule.objects.for_workspace(ws).filter(enabled=True).count()), "purple"),
        ("covered", "Competitors covered", str(len(competitor_selectors.header_list(request))), "teal"),
        ("latest", "Latest report", latest_val, "success"),
    ]
    return [
        {"id": i, "label": label, "value": value, "tone": tone, "icon": KPI_ICONS.get(i, "file-bar-chart-2")}
        for i, label, value, tone in values
    ]


def report_types():
    return REPORT_TYPES


def report_type(type_id):
    return next((t for t in REPORT_TYPES if t["id"] == type_id), None)


def _workspace(request):
    return getattr(request, "workspace", None)


def _pk(value):
    return int(value) if str(value).isdigit() else None


def report_dict(obj, now=None):
    now = now or timezone.now()
    cfg = obj.config or {}
    minutes = max(0, int((now - obj.created_at).total_seconds() // 60))
    return {
        "id": str(obj.pk),
        "name": obj.title,
        "type_id": obj.report_type,
        "type": cfg.get("type_title", obj.report_type),
        "competitors": obj.competitors,
        "period": obj.period,
        "created": relative_time(minutes),
        "status": obj.status,
        "data_through": cfg.get("data_through", ""),
        "category": cfg.get("category"),
        "change_type": cfg.get("change_type"),
        "ai_analysis": cfg.get("ai_analysis", True),
        "summary": obj.summary,
    }


def schedule_dict(obj):
    return {
        "id": str(obj.pk),
        "name": obj.name,
        "type_id": obj.report_type,
        "competitors": obj.competitors,
        "frequency": obj.frequency,
        "time": obj.run_time,
        "active": obj.enabled,
    }


def all_reports(request):
    now = timezone.now()
    return [report_dict(r, now) for r in Report.objects.for_workspace(_workspace(request))]


def by_id(request, report_id):
    obj = Report.objects.for_workspace(_workspace(request)).filter(pk=_pk(report_id)).first()
    return report_dict(obj) if obj else None


def all_schedules(request):
    return [schedule_dict(s) for s in ReportSchedule.objects.for_workspace(_workspace(request))]


def schedule_by_id(request, schedule_id):
    obj = ReportSchedule.objects.for_workspace(_workspace(request)).filter(
        pk=_pk(schedule_id)
    ).first()
    return schedule_dict(obj) if obj else None


def reports_with_types(request):
    """Rows joined with their library type (icon tile) — generated-reports-table.tsx ReportName."""
    return [{"r": r, "type": report_type(r["type_id"])} for r in all_reports(request)]


def schedules_with_types(request):
    return [{"s": s, "type": report_type(s["type_id"])} for s in all_schedules(request)]


# ---------------------------------------------------------------------------
# Create dialog form state

CREATE_DEFAULTS = {
    "type_id": REPORT_TYPES[0]["id"],
    "competitors": REPORT_FORM_OPTIONS["competitors"][0],
    "date_range": "Last 7 days",
    "category": REPORT_FORM_OPTIONS["categories"][0],
    "change_type": REPORT_FORM_OPTIONS["change_types"][0],
    "ai_analysis": True,
}


def create_initial(type_id=None, duplicate=None):
    """Initial create-dialog values; `duplicate` is a report row (reports.tsx duplicate())."""
    initial = dict(CREATE_DEFAULTS)
    if type_id and report_type(type_id):
        initial["type_id"] = type_id
    if duplicate:
        initial["type_id"] = duplicate["type_id"]
        initial["competitors"] = (
            REPORT_FORM_OPTIONS["competitors"][0]
            if duplicate["competitors"] == "All"
            else duplicate["competitors"]
        )
        if duplicate["period"] in REPORT_FORM_OPTIONS["date_ranges"]:
            initial["date_range"] = duplicate["period"]
        if duplicate.get("category"):
            initial["category"] = duplicate["category"]
        if duplicate.get("change_type"):
            initial["change_type"] = duplicate["change_type"]
        if duplicate.get("ai_analysis") is not None:
            initial["ai_analysis"] = duplicate["ai_analysis"]
    return initial


def create_form_context(initial):
    return {
        "initial": initial,
        "type_options": [{"value": t["id"], "label": t["title"]} for t in REPORT_TYPES],
        "competitor_options": REPORT_FORM_OPTIONS["competitors"],
        "date_range_options": REPORT_FORM_OPTIONS["date_ranges"],
        "category_options": REPORT_FORM_OPTIONS["categories"],
        "change_type_options": REPORT_FORM_OPTIONS["change_types"],
        "historical_since": REPORT_FORM_OPTIONS["historical_since"],
        "stages": GENERATION_STAGES,
    }


# ---------------------------------------------------------------------------
# Schedule dialog form state

SCHEDULE_DEFAULTS = {
    "type_id": REPORT_TYPES[0]["id"],
    "competitors": REPORT_FORM_OPTIONS["competitors"][0],
    "frequency": "Daily",
    "time": "08:00",
}


def schedule_initial(type_id=None, schedule=None):
    """Initial schedule-dialog values; edit mode reverse-maps the stored labels."""
    initial = dict(SCHEDULE_DEFAULTS)
    if type_id and report_type(type_id):
        initial["type_id"] = type_id
    if schedule:
        initial["type_id"] = schedule["type_id"]
        if schedule["competitors"] in REPORT_FORM_OPTIONS["competitors"]:
            initial["competitors"] = schedule["competitors"]
        initial["frequency"] = next(
            (k for k, label in FREQUENCY_LABELS.items() if label == schedule["frequency"]),
            "Daily",
        )
        initial["time"] = schedule["time"]
    return initial


def schedule_form_context(initial, schedule=None):
    return {
        "initial": initial,
        "schedule": schedule,
        "type_options": [{"value": t["id"], "label": t["title"]} for t in REPORT_TYPES],
        "competitor_options": REPORT_FORM_OPTIONS["competitors"],
        "frequency_options": REPORT_FORM_OPTIONS["frequencies"],
        "time_options": REPORT_FORM_OPTIONS["times"],
    }


# ---------------------------------------------------------------------------
# Report details (body always renders the detailed weekly dataset, as the
# prototype does — header metadata comes from the actual report record)

def empty_sections():
    return {
        "metrics": [], "competitor_comparison": [], "pricing": {"facts": [], "series": [], "ai_note": ""},
        "category_comparison": [], "stock": {"title": "Stock Intelligence", "facts": [], "ai_note": ""},
        "promotions": {"title": "Promotion Intelligence", "facts": [], "ai_note": ""},
        "catalogue": {"title": "Catalogue Intelligence", "facts": [], "ai_note": ""},
        "developments": [], "opportunities": [], "risks": [], "recommended_actions": [],
        "executive_summary": "", "key_takeaway": "",
    }


def report_sections(report_obj):
    return (report_obj.config or {}).get("sections") or empty_sections()


def detail_charts(sections):
    pricing = sections["pricing"]["series"]
    categories = sections["category_comparison"]
    return {
        "pricing": {
            "type": "line",
            "labels": [p["day"] for p in pricing],
            "series": [
                {"label": "Price decreases", "data": [p["decreases"] for p in pricing], "color": "success"},
                {"label": "Price increases", "data": [p["increases"] for p in pricing], "color": "destructive", "dashed": True},
            ],
            "options": {},
        },
        "category": {
            "type": "hbar",
            "labels": [c["name"] for c in categories],
            "series": [{"data": [c["changes"] for c in categories], "color": "chart-1"}],
            "options": {"labels": True, "barSize": 16, "labelWidth": 112},
        },
    }


def detail_metrics(sections):
    return [
        {**m, "icon": METRIC_ICONS.get(m["id"], "git-compare-arrows")}
        for m in sections["metrics"]
    ]


def ask_ai_href(report):
    qs = urlencode({"prompt": f"Summarise the key findings of {report['name']}"})
    return f"{reverse('ai:index')}?{qs}"


# ---------------------------------------------------------------------------
# CSV export — port of lib/report-csv.ts (weekly dataset as the mock body)

def report_csv_rows(report, sections):
    """Header + rows for the CSV export. Future: GET /api/reports/:id/export"""
    headers = ["Section", "Item", "Value", "", "", "", "", ""]
    meta = [
        ["Report", report["name"]],
        ["Type", report["type"]],
        ["Competitors", report["competitors"]],
        ["Period", report["period"]],
        ["Data through", report["data_through"]],
        [],
    ]
    metrics = [["Metric", m["label"], m["value"]] for m in sections["metrics"]]
    comparison = [
        [
            "Competitor",
            c["name"],
            f"changes={c['total']}",
            f"new={c['new_products']}",
            f"drops={c['drops']}",
            f"increases={c['increases']}",
            f"stockouts={c['stockouts']}",
            f"promos={c['promos']}",
        ]
        for c in sections["competitor_comparison"]
    ]
    return headers, [*meta, *metrics, *comparison]
