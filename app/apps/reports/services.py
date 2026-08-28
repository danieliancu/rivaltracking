"""Report mutations against the mock store.

Each function notes the future backend endpoint it stands in for
(services/reports.ts in the prototype).
"""
import time

from apps.core.mock.store import MockStore


def _base36(value):
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    while value:
        value, rem = divmod(value, 36)
        out = digits[rem] + out
    return out or "0"


def create_report(request, *, type_id, type_title, competitors, period,
                  category=None, change_type=None, ai_analysis=True):
    """Future: POST /api/reports → GeneratedReport (Report Engine + analytics).

    Port of workspace-store createReport + services/reports.ts generateReport:
    id "{typeId}-{Date.now base36}", name "{type} — {period}", created
    "Just now", status "ready", data through "26 Aug, 14:42"; prepended.
    """
    store = MockStore(request)
    report_id = f"{type_id}-{_base36(int(time.time() * 1000))}"
    existing = {r["id"] for r in store.get("reports")}
    while report_id in existing:  # same-millisecond regenerate clicks
        report_id += "0"
    report = {
        "id": report_id,
        "name": f"{type_title} — {period}",
        "type_id": type_id,
        "type": type_title,
        "competitors": competitors,
        "period": period,
        "created": "Just now",
        "status": "ready",
        "data_through": "26 Aug, 14:42",
        "category": category,
        "change_type": change_type,
        "ai_analysis": ai_analysis,
    }
    store.mutate("reports", lambda rows: rows.insert(0, report))
    return report


def delete_report(request, report_id):
    """Future: DELETE /api/reports/:id"""
    store = MockStore(request)
    store.replace("reports", [r for r in store.get("reports") if r["id"] != report_id])


def new_schedule_id(type_id):
    """schedule-report-dialog.tsx: `s-${typeId}-${Date.now().toString(36)}`."""
    return f"s-{type_id}-{_base36(int(time.time() * 1000))}"


def save_schedule(request, schedule):
    """Future: POST /api/report-schedules and PATCH /api/report-schedules/:id"""

    def _save(rows):
        for i, s in enumerate(rows):
            if s["id"] == schedule["id"]:
                rows[i] = schedule
                return
        rows.append(schedule)

    MockStore(request).mutate("report_schedules", _save)
    return schedule


def toggle_schedule(request, schedule_id):
    """Future: PATCH /api/report-schedules/:id (pause/resume)"""
    toggled = {}

    def _toggle(rows):
        for s in rows:
            if s["id"] == schedule_id:
                s["active"] = not s["active"]
                toggled.update(s)

    MockStore(request).mutate("report_schedules", _toggle)
    return toggled or None


def delete_schedule(request, schedule_id):
    """Future: DELETE /api/report-schedules/:id"""
    store = MockStore(request)
    store.replace(
        "report_schedules",
        [s for s in store.get("report_schedules") if s["id"] != schedule_id],
    )
