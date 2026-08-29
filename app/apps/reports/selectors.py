"""Report reads: store lookups, form option shaping, detail chart payloads."""
from urllib.parse import urlencode

from django.urls import reverse

from apps.core.store import WorkspaceStore

from .data import (
    GENERATION_STAGES,
    REPORT_FORM_OPTIONS,
    REPORT_KPIS,
    REPORT_TYPES,
    WEEKLY_REPORT,
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


def kpi_cards():
    return [{**k, "icon": KPI_ICONS.get(k["id"], "file-bar-chart-2")} for k in REPORT_KPIS]


def report_types():
    return REPORT_TYPES


def report_type(type_id):
    return next((t for t in REPORT_TYPES if t["id"] == type_id), None)


def all_reports(request):
    return WorkspaceStore(request).get("reports")


def by_id(request, report_id):
    return next((r for r in all_reports(request) if r["id"] == report_id), None)


def all_schedules(request):
    return WorkspaceStore(request).get("report_schedules")


def schedule_by_id(request, schedule_id):
    return next((s for s in all_schedules(request) if s["id"] == schedule_id), None)


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

def detail_charts():
    pricing = WEEKLY_REPORT["pricing"]["series"]
    categories = WEEKLY_REPORT["category_comparison"]
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


def detail_metrics():
    return [
        {**m, "icon": METRIC_ICONS.get(m["id"], "git-compare-arrows")}
        for m in WEEKLY_REPORT["metrics"]
    ]


def ask_ai_href(report):
    qs = urlencode({"prompt": f"Summarise the key findings of {report['name']}"})
    return f"{reverse('ai:index')}?{qs}"


# ---------------------------------------------------------------------------
# CSV export — port of lib/report-csv.ts (weekly dataset as the mock body)

def report_csv_rows(report):
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
    metrics = [["Metric", m["label"], m["value"]] for m in WEEKLY_REPORT["metrics"]]
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
        for c in WEEKLY_REPORT["competitor_comparison"]
    ]
    return headers, [*meta, *metrics, *comparison]
