"""Settings mutations against the Workspace/WorkspaceSettings/Membership models."""
import re

from apps.accounts.models import User, WorkspaceMembership
from apps.competitors.models import Competitor

WEBSITE_RE = re.compile(r"^https?://.+\..+")
EMAIL_RE = re.compile(r".+@.+\..+")

WORKSPACE_FIELDS = [
    "name", "website", "market", "industry", "currency", "timezone", "date_format",
]

# UI role label → membership role enum.
ROLE_LABEL_TO_ENUM = {
    "Admin": WorkspaceMembership.Role.ADMIN,
    "Member": WorkspaceMembership.Role.MEMBER,
}

JSON_SECTIONS = {"monitoring", "notifications", "ai", "reports"}


def _settings(request):
    return request.workspace.settings


def _set_path(target, path, value):
    keys = path.split(".")
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = value


def save_section(request, section, values):
    """Partial update of one settings section.

    Future: PATCH /api/settings/:section
    """
    ws = request.workspace
    s = _settings(request)

    if section == "workspace":
        ws.name = values.get("name", ws.name)
        ws.save(update_fields=["name", "updated_at"])
        for field in WORKSPACE_FIELDS[1:]:
            setattr(s, field, values.get(field, getattr(s, field)))
        s.save()
        return

    if section == "data":
        for path, value in values.items():
            if path == "retention":
                s.retention = value
        s.save(update_fields=["retention", "updated_at"])
        return

    if section in JSON_SECTIONS:
        payload = getattr(s, section) or {}
        for path, value in values.items():
            _set_path(payload, path, value)
        setattr(s, section, payload)
        s.save(update_fields=[section, "updated_at"])


def parse_autosave_post(request, section):
    """Turn an auto-saved control's POST into a partial-update values dict."""
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
            value = re.sub(r"\D", "", value)
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
    """Future: POST /api/team/invitations. Creates the user + membership."""
    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        user = User.objects.create_user(email=email, password=None)
    membership, _ = WorkspaceMembership.objects.get_or_create(
        user=user,
        workspace=request.workspace,
        defaults={"role": ROLE_LABEL_TO_ENUM.get(role, WorkspaceMembership.Role.MEMBER)},
    )
    return {
        "id": str(membership.id),
        "name": user.display_name,
        "email": user.email,
        "role": membership.get_role_display(),
    }


def _membership(request, member_id):
    try:
        return request.workspace.memberships.select_related("user").get(id=member_id)
    except (WorkspaceMembership.DoesNotExist, ValueError, TypeError):
        return None


def change_role(request, member_id, role):
    """Future: PATCH /api/team/:id. Owners are never demoted here."""
    membership = _membership(request, member_id)
    if membership is None or membership.is_owner:
        return None
    membership.role = ROLE_LABEL_TO_ENUM.get(role, membership.role)
    membership.save(update_fields=["role"])
    return {"name": membership.user.display_name}


def remove_member(request, member_id):
    """Future: DELETE /api/team/:id. Owners cannot be removed."""
    membership = _membership(request, member_id)
    if membership is not None and not membership.is_owner:
        membership.delete()


# ---------------------------------------------------------------------------
# Data & Privacy


def delete_competitor_data(request, name):
    """Future: DELETE /api/data/competitors/:slug.

    Deleting the Competitor cascades its listings, snapshots, promotions and
    change events; canonical products remain.
    """
    Competitor.objects.for_workspace(request.workspace).filter(name=name).delete()


def delete_workspace(request):
    """Future: DELETE /api/workspace.

    Demo affordance: rebuild the workspace's seed data rather than destroying
    the tenant (which would sign the user out mid-demo).
    """
    from apps.core.seed import seed_workspace

    seed_workspace(request.workspace)
