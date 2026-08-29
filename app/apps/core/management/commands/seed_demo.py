"""Seed a realistic demo workspace exercising every Phase 1 screen.

    python manage.py seed_demo            # create/refresh the demo workspace
    python manage.py seed_demo --reset    # also reset the demo user's password

Idempotent: the demo user, workspace and membership are get_or_created and the
business data is fully rebuilt on each run (see apps.core.seed.seed_workspace).
"""
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User, WorkspaceMembership
from apps.accounts.services import create_workspace
from apps.core.seed import seed_workspace

DEMO_WORKSPACE_NAME = "Acme Toys Ltd"
DEMO_WORKSPACE_SLUG = "acme-toys"


class Command(BaseCommand):
    help = "Seed the demo workspace with competitors, products, history and events."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Re-seed the demo workspace (data is rebuilt every run regardless).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        email = settings.DEMO_EMAIL

        user, created = User.objects.get_or_create(
            email=email,
            defaults={"first_name": "Demo", "last_name": "User", "is_staff": False},
        )
        if created:
            # No demo password exists; the demo user signs in only via the
            # password-less "Enter the demo" button (gated by DEMO_LOGIN_ENABLED).
            user.set_unusable_password()
            user.save()

        workspace = user.workspaces.filter(slug=DEMO_WORKSPACE_SLUG).first()
        if workspace is None:
            # Reuse a pre-existing slug (fresh install) or make the workspace.
            from apps.accounts.models import Workspace

            workspace = Workspace.objects.filter(slug=DEMO_WORKSPACE_SLUG).first()
            if workspace is None:
                workspace = create_workspace(
                    DEMO_WORKSPACE_NAME, owner=user, slug=DEMO_WORKSPACE_SLUG
                )
            WorkspaceMembership.objects.get_or_create(
                user=user,
                workspace=workspace,
                defaults={"role": WorkspaceMembership.Role.OWNER},
            )

        seed_workspace(workspace)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded '{workspace.name}' for {email}. "
                "Use the 'Enter the demo' button on the login page."
            )
        )
