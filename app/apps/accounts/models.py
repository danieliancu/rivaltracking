"""Identity and tenancy models: User, Workspace, membership and settings.

Every business object in RivalTracking belongs to a Workspace (directly or
through a related object). A User reaches a Workspace through a
WorkspaceMembership, which also carries the user's role in that workspace.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    """Email-authenticated user (no username field)."""

    username = None
    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return self.email

    @property
    def display_name(self):
        return self.get_full_name() or self.email

    @property
    def initials(self):
        full = self.get_full_name().strip()
        if full:
            parts = full.split()
            letters = (parts[0][0] + parts[-1][0]) if len(parts) > 1 else parts[0][:2]
        else:
            letters = self.email[:2]
        return letters.upper()


class Workspace(models.Model):
    """One customer/company account — the tenant boundary."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    members = models.ManyToManyField(
        User, through="WorkspaceMembership", related_name="workspaces"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class WorkspaceMembership(models.Model):
    """Links a User to a Workspace with a role.

    Roles are intentionally a small closed set for Phase 2; the TextChoices
    enum is the single place to widen them (e.g. analyst/viewer) later.
    """

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="memberships"
    )
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.MEMBER
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "workspace"], name="unique_user_workspace"
            )
        ]
        ordering = ["workspace_id", "user_id"]

    def __str__(self):
        return f"{self.user} @ {self.workspace} ({self.role})"

    @property
    def is_owner(self):
        return self.role == self.Role.OWNER

    @property
    def can_manage(self):
        return self.role in {self.Role.OWNER, self.Role.ADMIN}


class WorkspaceSettings(models.Model):
    """Per-workspace configuration backing the Settings pages.

    Profile fields are columns; the toggle-heavy sections (monitoring,
    notifications, AI, reports) live in JSON so the Settings UI's dotted-path
    autosave keeps working without a column per switch.
    """

    workspace = models.OneToOneField(
        Workspace, on_delete=models.CASCADE, related_name="settings"
    )
    website = models.URLField(blank=True)
    market = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=64, blank=True)
    date_format = models.CharField(max_length=20, blank=True)

    monitoring = models.JSONField(default=dict, blank=True)
    notifications = models.JSONField(default=dict, blank=True)
    ai = models.JSONField(default=dict, blank=True)
    reports = models.JSONField(default=dict, blank=True)
    retention = models.JSONField(default=dict, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.workspace}"
