"""Mutations for identity and tenancy."""
from django.db import transaction
from django.utils.text import slugify

from apps.core.entities import slugify as domain_slugify

from .models import User, Workspace, WorkspaceMembership, WorkspaceSettings
from .selectors import ACTIVE_WORKSPACE_SESSION_KEY


def unique_workspace_slug(name):
    """A workspace slug unique across all tenants."""
    base = slugify(name) or "workspace"
    slug = base
    i = 2
    while Workspace.objects.filter(slug=slug).exists():
        slug = f"{base}-{i}"
        i += 1
    return slug


def default_settings_payload(name):
    """Seed a new workspace's settings from the Phase 1 defaults."""
    from apps.settings_app import data as s

    return {
        "website": "",
        "market": s.WORKSPACE_SETTINGS.get("market", ""),
        "industry": s.WORKSPACE_SETTINGS.get("industry", ""),
        "currency": s.WORKSPACE_SETTINGS.get("currency", "GBP (£)"),
        "timezone": s.WORKSPACE_SETTINGS.get("timezone", "Europe/London"),
        "date_format": s.WORKSPACE_SETTINGS.get("date_format", "DD/MM/YYYY"),
        "monitoring": dict(s.MONITORING_SETTINGS),
        "notifications": dict(s.NOTIFICATION_SETTINGS),
        "ai": dict(s.AI_SETTINGS),
        "reports": dict(s.REPORT_SETTINGS),
        "retention": {"competitor_data": "12 months", "reports": "24 months"},
    }


@transaction.atomic
def create_workspace(name, *, owner=None, slug=None):
    """Create a Workspace with default settings and (optionally) an owner."""
    workspace = Workspace.objects.create(
        name=name, slug=slug or unique_workspace_slug(name)
    )
    WorkspaceSettings.objects.create(workspace=workspace, **default_settings_payload(name))
    if owner is not None:
        WorkspaceMembership.objects.create(
            user=owner, workspace=workspace, role=WorkspaceMembership.Role.OWNER
        )
    return workspace


@transaction.atomic
def register_account(*, email, password, first_name="", last_name="", workspace_name=None):
    """Self-service signup: create the user, their workspace and owner membership."""
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
    )
    workspace_name = (workspace_name or "").strip() or (
        f"{first_name.strip()}'s workspace" if first_name.strip() else "My workspace"
    )
    workspace = create_workspace(workspace_name, owner=user)
    return user, workspace


def set_active_workspace(request, workspace_id):
    """Switch the request's active workspace (validated against membership)."""
    if WorkspaceMembership.objects.filter(
        user=request.user, workspace_id=workspace_id
    ).exists():
        request.session[ACTIVE_WORKSPACE_SESSION_KEY] = workspace_id
        return True
    return False
