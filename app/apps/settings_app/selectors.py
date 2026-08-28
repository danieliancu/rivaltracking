"""Settings reads over the mock store (port of settings sections' derived state)."""
from django.utils import timezone

from apps.core.mock.store import MockStore

from . import data

SECTION_IDS = [s["id"] for s in data.SETTINGS_SECTIONS]

ASSIGNABLE_ROLES = ["Admin", "Analyst", "Viewer"]


def settings_state(request):
    """The full settings dict, with the top-level retention default applied."""
    stored = MockStore(request).get("settings")
    state = dict(stored)
    state.setdefault("retention", data.DATA_SETTINGS["retention"])
    return state


def _labelled_toggles(values, labels):
    return [
        {"key": key, "label": labels[key], "checked": on}
        for key, on in values.items()
    ]


def initials(name):
    """team-section.tsx avatar: first letters of the first two name/dot parts."""
    parts = [p for p in name.replace(".", " ").split() if p]
    return "".join(p[0].upper() for p in parts[:2])


def team_rows(request):
    return [
        {**m, "initials": initials(m["name"])}
        for m in settings_state(request)["team"]
    ]


def member_by_id(request, member_id):
    for m in team_rows(request):
        if m["id"] == member_id:
            return m
    return None


def competitor_names(request):
    """data-section.tsx: live competitor names, falling back to the seed list."""
    from apps.competitors.selectors import all_rows

    names = [c["name"] for c in all_rows(request)]
    return names if names else list(data.DATA_SETTINGS["competitors"])


def billing_usage():
    return [
        {**u, "percent": min(100, u["used"] / u["limit"] * 100)}
        for u in data.BILLING["usage"]
    ]


def export_snapshot(request):
    """workspace-store.tsx exportWorkspaceSnapshot — portable workspace JSON."""
    store = MockStore(request)
    return {
        "exported_at": timezone.now().isoformat(),
        "workspace": settings_state(request)["workspace"],
        "competitors": store.get("competitors"),
        "products": store.get("products"),
        "change_events": [
            {
                **{k: v for k, v in e.items() if k != "product"},
                "product": {
                    "slug": e["product"]["slug"],
                    "name": e["product"]["name"],
                    "sku": e["product"]["sku"],
                },
            }
            for e in store.get("change_events")
        ],
        "reports": store.get("reports"),
        "report_schedules": store.get("report_schedules"),
        "watchlist": list(store.get("watchlist")),
    }


def section_context(request, section):
    """Everything the active section's partial needs."""
    state = settings_state(request)
    ctx = {"settings": state}
    if section == "workspace":
        ctx.update(workspace=state["workspace"], options=data.WORKSPACE_OPTIONS)
    elif section == "monitoring":
        m = state["monitoring"]
        ctx.update(
            m=m,
            frequency_options=["Every 24 hours", "Every 12 hours", "Every 6 hours"],
            scope_items=_labelled_toggles(m["scope"], data.MONITORING_SCOPE_LABELS),
            advanced_items=_labelled_toggles(
                m["advanced_scope"], data.MONITORING_SCOPE_LABELS
            ),
        )
    elif section == "notifications":
        n = state["notifications"]
        ctx.update(
            n=n,
            priority_items=[
                {"key": p, "label": f"{p.capitalize()} priority", "checked": n["priorities"][p]}
                for p in ("high", "medium", "low")
            ],
            email_option_items=_labelled_toggles(
                n["email_options"], data.EMAIL_OPTION_LABELS
            ),
            time_options=["06:00", "08:00", "12:00", "18:00"],
            day_options=["Monday", "Friday", "Sunday"],
        )
    elif section == "ai":
        ctx.update(ai=state["ai"], style_options=data.AI_STYLE_OPTIONS)
    elif section == "reports":
        ctx.update(
            r=state["reports"],
            detail_options=data.REPORT_DETAIL_OPTIONS,
            period_options=["Today", "Last 7 days", "Last 30 days"],
            competitor_options=[
                "All monitored competitors",
                "ToyWorld.co.uk",
                "PlayNest.co.uk",
                "HappyToyHouse.com",
                "LittleMindsToys.co.uk",
            ],
            daily_time_options=["06:00", "08:00", "12:00"],
            weekly_day_options=["Monday", "Friday"],
            weekly_time_options=["06:00", "08:00", "16:00"],
        )
    elif section == "team":
        ctx.update(
            members=team_rows(request),
            role_descriptions=data.ROLE_DESCRIPTIONS,
            assignable_roles=ASSIGNABLE_ROLES,
        )
    elif section == "data":
        ctx.update(
            stats=data.DATA_SETTINGS["stats"],
            retention=state["retention"],
            retention_options=data.DATA_SETTINGS["retention_options"],
        )
    elif section == "billing":
        ctx.update(billing=data.BILLING, usage=billing_usage())
    return ctx
