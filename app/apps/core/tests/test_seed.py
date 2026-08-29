"""The seed_demo management command is idempotent and populates a workspace."""
import pytest
from django.core.management import call_command

from apps.accounts.models import User, Workspace, WorkspaceMembership
from apps.catalogue.models import PriceSnapshot, Product, ProductListing
from apps.changes.models import ChangeEvent
from apps.competitors.models import Competitor

pytestmark = pytest.mark.django_db


def test_seed_demo_populates_workspace():
    call_command("seed_demo")

    user = User.objects.get(email="demo@rivaltracking.com")
    workspace = Workspace.objects.get(slug="acme-toys")
    assert WorkspaceMembership.objects.filter(
        user=user, workspace=workspace, role=WorkspaceMembership.Role.OWNER
    ).exists()

    assert Competitor.objects.filter(workspace=workspace).count() == 4
    assert Product.objects.filter(workspace=workspace).count() == 10
    assert ProductListing.objects.filter(workspace=workspace).count() >= 10
    assert ChangeEvent.objects.filter(workspace=workspace).count() == 9
    assert PriceSnapshot.objects.filter(workspace=workspace).exists()


def test_seed_demo_is_idempotent():
    call_command("seed_demo")
    call_command("seed_demo")

    assert User.objects.filter(email="demo@rivaltracking.com").count() == 1
    assert Workspace.objects.filter(slug="acme-toys").count() == 1
    workspace = Workspace.objects.get(slug="acme-toys")
    assert Competitor.objects.filter(workspace=workspace).count() == 4
    assert ChangeEvent.objects.filter(workspace=workspace).count() == 9
