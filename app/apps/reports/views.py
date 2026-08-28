import csv
import io

from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django_htmx.http import HttpResponseClientRedirect
from django.urls import reverse

from .data import GENERATION_STAGES, REPORT_FORM_OPTIONS, WEEKLY_REPORT
from . import selectors, services


def _generated_context(request, toast=None):
    return {"generated": selectors.reports_with_types(request), "toast": toast}


def _scheduled_context(request, toast=None):
    return {"scheduled": selectors.schedules_with_types(request), "toast": toast}


def index(request):
    context = {
        "kpis": selectors.kpi_cards(),
        "library": selectors.report_types(),
        **_generated_context(request),
        **_scheduled_context(request),
    }
    # Deep links (React router-state → query params): /reports?create=<typeId>
    # opens the create dialog; ?schedule=1 opens the schedule dialog.
    create_param = request.GET.get("create")
    if create_param:
        context["open_create"] = selectors.create_form_context(
            selectors.create_initial(type_id=create_param)
        )
    elif request.GET.get("schedule"):
        context["open_schedule"] = selectors.schedule_form_context(
            selectors.schedule_initial()
        )
    return render(request, "reports/index.html", context)


# ---------------------------------------------------------------------------
# Create report

def create_dialog(request):
    """Create-report dialog fragment (HTMX → #modal-root).

    ?type=<id> preselects a library type; ?duplicate=<reportId> prefills the
    whole configuration from an existing report (reports.tsx duplicate())."""
    duplicate = None
    if request.GET.get("duplicate"):
        duplicate = selectors.by_id(request, request.GET["duplicate"])
    initial = selectors.create_initial(
        type_id=request.GET.get("type"), duplicate=duplicate
    )
    return render(
        request,
        "reports/partials/create_dialog.html",
        selectors.create_form_context(initial),
    )


@require_POST
def create(request):
    """Create a report and return the staged 'generating' dialog phase."""
    type_ = selectors.report_type(request.POST.get("type_id")) or selectors.report_types()[0]
    competitors = request.POST.get("competitors") or REPORT_FORM_OPTIONS["competitors"][0]
    category = request.POST.get("category")
    change_type = request.POST.get("change_type")
    report = services.create_report(
        request,
        type_id=type_["id"],
        type_title=type_["title"],
        competitors="All" if competitors == REPORT_FORM_OPTIONS["competitors"][0] else competitors,
        period=request.POST.get("date_range") or "Last 7 days",
        category=None if category in (None, REPORT_FORM_OPTIONS["categories"][0]) else category,
        change_type=None if change_type in (None, REPORT_FORM_OPTIONS["change_types"][0]) else change_type,
        ai_analysis=request.POST.get("ai_analysis") is not None,
    )
    return render(
        request,
        "reports/partials/create_generating.html",
        {
            "report": report,
            "stages": GENERATION_STAGES,
            "toast": {
                "variant": "success",
                "title": "Report generated",
                "description": report["name"],
            },
        },
    )


def generated_fragment(request):
    """Generated Reports card fragment (refreshed on reports:changed)."""
    return render(
        request, "reports/partials/generated_reports.html", _generated_context(request)
    )


@require_POST
def delete(request, report_id):
    report = selectors.by_id(request, report_id)
    if report is None:
        raise Http404
    services.delete_report(request, report_id)
    return render(
        request,
        "reports/partials/generated_reports.html",
        _generated_context(
            request,
            toast={"variant": "info", "title": "Report deleted", "description": report["name"]},
        ),
    )


@require_POST
def download_pdf(request, report_id):
    """PDF stub — the prototype only raises an informational toast."""
    report = selectors.by_id(request, report_id)
    if report is None:
        raise Http404
    description = (
        "Export to CSV is available in the meantime."
        if request.GET.get("detail")
        else f"{report['name']} can be exported to CSV in the meantime."
    )
    return render(
        request,
        "partials/toast.html",
        {
            "variant": "info",
            "title": "PDF generation will be handled by the report backend.",
            "description": description,
        },
    )


def export_csv(request, report_id):
    """CSV export — port of lib/report-csv.ts + lib/csv.ts."""
    report = selectors.by_id(request, report_id)
    if report is None:
        raise Http404
    headers, rows = selectors.report_csv_rows(report)
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")  # quotes on , " \n like csv.ts
    writer.writerow(headers)
    writer.writerows(rows)
    response = HttpResponse(
        buffer.getvalue().rstrip("\n"), content_type="text/csv; charset=utf-8"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="rivaltracking-report-{report["id"]}.csv"'
    )
    return response


@require_POST
def regenerate(request, report_id):
    """Create a fresh version of a report and redirect to its detail page."""
    report = selectors.by_id(request, report_id)
    if report is None:
        raise Http404
    fresh = services.create_report(
        request,
        type_id=report["type_id"],
        type_title=report["type"],
        competitors=report["competitors"],
        period=report["period"],
        category=report.get("category"),
        change_type=report.get("change_type"),
        ai_analysis=report.get("ai_analysis", True),
    )
    return HttpResponseClientRedirect(reverse("reports:detail", args=[fresh["id"]]))


# ---------------------------------------------------------------------------
# Scheduled reports

def schedule_dialog(request):
    """Schedule-report dialog fragment (HTMX → #modal-root).

    ?type=<id> preselects a report type; ?edit=<scheduleId> edits in place."""
    schedule = None
    if request.GET.get("edit"):
        schedule = selectors.schedule_by_id(request, request.GET["edit"])
    initial = selectors.schedule_initial(
        type_id=request.GET.get("type"), schedule=schedule
    )
    return render(
        request,
        "reports/partials/schedule_dialog.html",
        selectors.schedule_form_context(initial, schedule=schedule),
    )


@require_POST
def save_schedule(request):
    existing = None
    if request.POST.get("schedule_id"):
        existing = selectors.schedule_by_id(request, request.POST["schedule_id"])
    type_ = selectors.report_type(request.POST.get("type_id")) or selectors.report_types()[0]
    competitors = request.POST.get("competitors") or REPORT_FORM_OPTIONS["competitors"][0]
    schedule = {
        "id": existing["id"] if existing else services.new_schedule_id(type_["id"]),
        "name": type_["title"],
        "type_id": type_["id"],
        "frequency": selectors.FREQUENCY_LABELS.get(
            request.POST.get("frequency"), "Every day"
        ),
        "time": request.POST.get("time") or "08:00",
        "competitors": (
            "All competitors"
            if competitors == REPORT_FORM_OPTIONS["competitors"][0]
            else competitors
        ),
        "active": existing["active"] if existing else True,
    }
    services.save_schedule(request, schedule)
    return render(
        request,
        "reports/partials/scheduled_reports.html",
        _scheduled_context(
            request,
            toast={
                "variant": "success",
                "title": "Schedule updated" if existing else "Report scheduled",
                "description": f"{schedule['name']} · {schedule['frequency']} at {schedule['time']}",
            },
        ),
    )


@require_POST
def toggle_schedule(request, schedule_id):
    schedule = services.toggle_schedule(request, schedule_id)
    if schedule is None:
        raise Http404
    return render(
        request,
        "reports/partials/scheduled_reports.html",
        _scheduled_context(
            request,
            toast={
                "variant": "info",
                "title": "Schedule resumed" if schedule["active"] else "Schedule paused",
                "description": schedule["name"],
            },
        ),
    )


@require_POST
def delete_schedule(request, schedule_id):
    schedule = selectors.schedule_by_id(request, schedule_id)
    if schedule is None:
        raise Http404
    services.delete_schedule(request, schedule_id)
    return render(
        request,
        "reports/partials/scheduled_reports.html",
        _scheduled_context(
            request,
            toast={"variant": "info", "title": "Schedule deleted", "description": schedule["name"]},
        ),
    )


# ---------------------------------------------------------------------------
# Report details

def detail(request, report_id):
    report = selectors.by_id(request, report_id)
    if report is None:
        return render(request, "reports/detail.html", {"report": None})
    return render(
        request,
        "reports/detail.html",
        {
            "report": report,
            "r": WEEKLY_REPORT,
            "metrics": selectors.detail_metrics(),
            "charts": selectors.detail_charts(),
            "ask_ai_href": selectors.ask_ai_href(report),
        },
    )
