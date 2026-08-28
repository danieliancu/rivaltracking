"""Settings mutations against the mock store."""
import re

from apps.core.mock.store import MockStore

WEBSITE_RE = re.compile(r"^https?://.+\..+")
EMAIL_RE = re.compile(r".+@.+\..+")

WORKSPACE_FIELDS = [
    "name", "website", "market", "industry", "currency", "timezone", "date_format",
]


def _set_path(target, path, value):
    keys = path.split(".")
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = value


def save_section(request, section, values):
    """Future: PATCH /api/settings/:section

    Partial update: `values` maps (dotted) field paths to new values.
    Section "data" writes top-level settings keys (retention).
    """

    def _apply(settings):
        target = settings if section == "data" else settings.setdefault(section, {})
        for path, value in values.items():
            _set_path(target, path, value)

    MockStore(request).mutate("settings", _apply)


def parse_autosave_post(request, section):
    """Turn an auto-saved control's POST into a partial-update values dict.

    Toggle rows post `field=<dotted path>` plus the checkbox pair only when
    checked; selects/inputs post plain name=value pairs.
    """
    post = request.POST
    if "field" in post:
        path = post["field"]
        return {path: post.get(path) is not None}
    values = {}
    for key in post.keys():
        if key in ("csrfmiddlewaretoken", "field"):
            continue
        value = post[key]
        if section == "monitoring" and key == "ignore_threshold":
            value = re.sub(r"\D", "", value)  # monitoring-section.tsx replace(/\D/g, "")
        values[key] = value
    return values


def parse_workspace_post(request):
    """Workspace explicit save: all seven fields + website validation."""
    values = {f: request.POST.get(f, "") for f in WORKSPACE_FIELDS}
    website_error = None
    if values["website"] and not WEBSITE_RE.match(values["website"]):
        website_error = "Enter a valid website"
    return values, website_error


# ---------------------------------------------------------------------------
# Team


def invite_member(request, email, role):
    """Future: POST /api/team/invitations"""
    member = {
        "id": f"m-{email}",
        "name": email.split("@")[0],
        "email": email,
        "role": role,
        "status": "Invited",
        "last_active": "—",
    }

    def _append(settings):
        settings["team"].append(member)

    MockStore(request).mutate("settings", _append)
    return member


def change_role(request, member_id, role):
    """Future: PATCH /api/team/:id"""
    changed = None

    def _change(settings):
        nonlocal changed
        for m in settings["team"]:
            if m["id"] == member_id:
                m["role"] = role
                changed = m

    MockStore(request).mutate("settings", _change)
    return changed


def remove_member(request, member_id):
    """Future: DELETE /api/team/:id"""

    def _remove(settings):
        settings["team"] = [m for m in settings["team"] if m["id"] != member_id]

    MockStore(request).mutate("settings", _remove)


# ---------------------------------------------------------------------------
# Data & Privacy


def delete_competitor_data(request, name):
    """Future: DELETE /api/data/competitors/:slug

    Removes the competitor's products, change events and competitor row.
    """
    store = MockStore(request)
    store.replace(
        "products", [p for p in store.get("products") if p["competitor"] != name]
    )
    store.replace(
        "change_events",
        [e for e in store.get("change_events") if e["competitor"] != name],
    )
    store.replace(
        "competitors", [c for c in store.get("competitors") if c["name"] != name]
    )


def delete_workspace(request):
    """Future: DELETE /api/workspace — resets the demo workspace."""
    MockStore(request).reset()
