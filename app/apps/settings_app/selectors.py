"""Settings reads over the real Workspace/WorkspaceSettings/Membership models.

`settings_state` rebuilds the nested settings dict the Phase 1 templates
consumed from the workspace's profile columns, the JSON toggle sections and the
membership table, so the section partials are unchanged.
"""
from django.utils import timezone

from apps.changes import selectors as change_selectors
from apps.competitors import selectors as competitor_selectors
from apps.products import selectors as product_selectors

from . import data

SECTION_IDS = [s["id"] for s in data.SETTINGS_SECTIONS]

# Roles a manager can assign (Owner is not assignable). Maps the UI label to
# the WorkspaceMembership.Role enum.
ASSIGNABLE_ROLES = ["Admin", "Member"]


def _settings(request):
    return request.workspace.settings


def settings_state(request):
    """The full settings dict the section partials expect."""
    ws = request.workspace
    s = _settings(request)
    return {
        "workspace": {
            "name": ws.name,
            "website": s.website,
            "market": s.market,
            "industry": s.industry,
            "currency": s.currency,
            "timezone": s.timezone,
            "date_format": s.date_format,
        },
        "monitoring": s.monitoring or dict(data.MONITORING_SETTINGS),
        "notifications": s.notifications or dict(data.NOTIFICATION_SETTINGS),
        "ai": s.ai or dict(data.AI_SETTINGS),
        "reports": s.reports or dict(data.REPORT_SETTINGS),
        "team": _team_members(request),
        "retention": s.retention or data.DATA_SETTINGS["retention"],
    }


def _labelled_toggles(values, labels):
    return [{"key": key, "label": labels[key], "checked": on} for key, on in values.items()]


def initials(name):
    parts = [p for p in name.replace(".", " ").split() if p]
    return "".join(p[0].upper() for p in parts[:2])


def _last_active(user):
    if user.last_login:
        minutes = max(0, int((timezone.now() - user.last_login).total_seconds() // 60))
        from apps.core.format import relative_time

        return relative_time(minutes)
    return "—"


def _team_members(request):
    rows = []
    for m in request.workspace.memberships.select_related("user").order_by("created_at"):
        user = m.user
        rows.append(
            {
                "id": str(m.id),
                "name": user.display_name,
                "email": user.email,
                "role": m.get_role_display(),
                "status": "Active",
                "last_active": _last_active(user),
                "is_owner": m.is_owner,
            }
        )
    return rows


def team_rows(request):
    return [{**m, "initials": initials(m["name"])} for m in _team_members(request)]


def member_by_id(request, member_id):
    for m in team_rows(request):
        if m["id"] == str(member_id):
            return m
    return None


def competitor_names(request):
    names = [c["name"] for c in competitor_selectors.header_list(request)]
    return names if names else list(data.DATA_SETTINGS["competitors"])


def billing_usage():
    return [
        {**u, "percent": min(100, u["used"] / u["limit"] * 100)}
        for u in data.BILLING["usage"]
    ]


def export_snapshot(request):
    """Portable workspace JSON, now assembled from the ORM."""
    return {
        "exported_at": timezone.now().isoformat(),
        "workspace": settings_state(request)["workspace"],
        "competitors": competitor_selectors.all_rows(request),
        "products": product_selectors.all_rows(request),
        "change_events": [
            {
                **{k: v for k, v in e.items() if k != "product"},
                "product": {
                    "slug": e["product"]["slug"],
                    "name": e["product"]["name"],
                    "sku": e["product"]["sku"],
                },
            }
            for e in change_selectors.all_events(request)
        ],
        "watchlist": list(product_selectors.watchlist(request)),
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
            competitor_options=["All monitored competitors", *competitor_names(request)],
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
