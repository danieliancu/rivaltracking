"""Authentication, signup, membership and model-constraint tests."""
import pytest
from django.db import IntegrityError, transaction
from django.urls import reverse

from apps.accounts.models import User, Workspace, WorkspaceMembership
from apps.catalogue.models import Product
from apps.products.models import WatchlistItem

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Gating

def test_anonymous_is_redirected_to_login(anon_client):
    response = anon_client.get(reverse("competitors:index"))
    assert response.status_code == 302
    assert reverse("accounts:login") in response["Location"]
    assert "next=" in response["Location"]


def test_login_page_public(anon_client):
    response = anon_client.get(reverse("accounts:login"))
    assert response.status_code == 200
    assert "Sign in" in response.content.decode()


# ---------------------------------------------------------------------------
# Login / logout

def test_login_success(anon_client, owner_user):
    response = anon_client.post(
        reverse("accounts:login"),
        {"email": "owner@demo.test", "password": "owner-pass-12345"},
    )
    assert response.status_code == 302
    assert response["Location"] == reverse("dashboard:overview")


def test_login_is_case_insensitive_on_email(anon_client, owner_user):
    response = anon_client.post(
        reverse("accounts:login"),
        {"email": "OWNER@DEMO.TEST", "password": "owner-pass-12345"},
    )
    assert response.status_code == 302


def test_login_invalid_password(anon_client, owner_user):
    response = anon_client.post(
        reverse("accounts:login"),
        {"email": "owner@demo.test", "password": "wrong"},
    )
    assert response.status_code == 200
    assert "Invalid email or password." in response.content.decode()


def test_logout(client):
    response = client.post(reverse("accounts:logout"))
    assert response.status_code == 302
    assert response["Location"] == reverse("accounts:login")
    # Subsequent access is gated again.
    assert client.get(reverse("competitors:index")).status_code == 302


# ---------------------------------------------------------------------------
# Signup

def test_signup_creates_user_workspace_and_owner(anon_client):
    response = anon_client.post(
        reverse("accounts:signup"),
        {
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
            "workspace_name": "Analytical Engines",
            "password1": "sup3r-secret-pw",
            "password2": "sup3r-secret-pw",
        },
    )
    assert response.status_code == 302
    user = User.objects.get(email="ada@example.com")
    workspace = Workspace.objects.get(name="Analytical Engines")
    membership = WorkspaceMembership.objects.get(user=user, workspace=workspace)
    assert membership.role == WorkspaceMembership.Role.OWNER
    # Signup logs the user in.
    assert anon_client.get(reverse("dashboard:overview")).status_code == 200


def test_signup_rejects_duplicate_email(anon_client, owner_user):
    response = anon_client.post(
        reverse("accounts:signup"),
        {
            "email": "owner@demo.test",
            "password1": "sup3r-secret-pw",
            "password2": "sup3r-secret-pw",
        },
    )
    assert response.status_code == 200
    assert "already exists" in response.content.decode()


def test_signup_rejects_mismatched_passwords(anon_client):
    response = anon_client.post(
        reverse("accounts:signup"),
        {
            "email": "mismatch@example.com",
            "password1": "sup3r-secret-pw",
            "password2": "different-pw-99",
        },
    )
    assert response.status_code == 200
    assert not User.objects.filter(email="mismatch@example.com").exists()


# ---------------------------------------------------------------------------
# Demo login

def test_demo_login_without_seed_shows_error(anon_client, db):
    response = anon_client.post(reverse("accounts:demo_login"))
    assert response.status_code == 200
    assert "Demo account is not available" in response.content.decode()


# ---------------------------------------------------------------------------
# Model constraints

def test_email_is_the_username_field():
    assert User.USERNAME_FIELD == "email"


def test_competitor_slug_unique_per_workspace(workspace):
    from apps.competitors.models import Competitor

    Competitor.objects.create(workspace=workspace, name="Dup A", slug="dup")
    with pytest.raises(IntegrityError), transaction.atomic():
        Competitor.objects.create(workspace=workspace, name="Dup B", slug="dup")


def test_membership_unique_per_user_workspace(workspace, owner_user):
    with pytest.raises(IntegrityError), transaction.atomic():
        WorkspaceMembership.objects.create(
            user=owner_user, workspace=workspace, role=WorkspaceMembership.Role.MEMBER
        )


def test_watchlist_unique_per_workspace(workspace):
    product = Product.objects.for_workspace(workspace).first()
    WatchlistItem.objects.create(workspace=workspace, product=product)
    with pytest.raises(IntegrityError), transaction.atomic():
        WatchlistItem.objects.create(workspace=workspace, product=product)


def test_user_may_belong_to_multiple_workspaces(owner_user, other_workspace):
    WorkspaceMembership.objects.create(
        user=owner_user, workspace=other_workspace, role=WorkspaceMembership.Role.MEMBER
    )
    assert owner_user.workspaces.count() == 2
