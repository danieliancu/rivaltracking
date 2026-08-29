"""Shared pytest fixtures for the Phase 2 (auth + multi-tenant) test suite.

The whole app is login-gated, so the default ``client`` is overridden to be
signed in as the owner of a freshly seeded demo workspace — existing page/
fragment tests keep working with the same ``client.get(...)`` calls. Use
``anon_client`` for auth-flow tests and ``other_client`` / ``other_workspace``
for tenant-isolation tests.
"""
import pytest
from django.test import Client

from apps.accounts.selectors import ACTIVE_WORKSPACE_SESSION_KEY
from apps.accounts.services import register_account
from apps.core.seed import seed_workspace


def _make_client(user, workspace):
    client = Client()
    client.force_login(user)
    session = client.session
    session[ACTIVE_WORKSPACE_SESSION_KEY] = workspace.id
    session.save()
    return client


@pytest.fixture
def workspace(db):
    """A seeded demo workspace ("Acme Toys Ltd") owned by owner_user."""
    user, ws = register_account(
        email="owner@demo.test",
        password="owner-pass-12345",
        first_name="Dani",
        last_name="Iancu",
        workspace_name="Acme Toys Ltd",
    )
    seed_workspace(ws)
    ws._owner = user
    return ws


@pytest.fixture
def owner_user(workspace):
    return workspace.memberships.select_related("user").first().user


@pytest.fixture
def client(workspace, owner_user):
    """Override pytest-django's client: signed in on the seeded workspace."""
    return _make_client(owner_user, workspace)


@pytest.fixture
def anon_client(db):
    """A logged-out client (for login/signup/password-reset tests)."""
    return Client()


@pytest.fixture
def other_workspace(db):
    """A second, separately-seeded workspace for isolation tests."""
    user, ws = register_account(
        email="rival@demo.test",
        password="rival-pass-12345",
        workspace_name="Rival Retail Ltd",
    )
    seed_workspace(ws)
    ws._owner = user
    return ws


@pytest.fixture
def other_client(other_workspace):
    return _make_client(other_workspace._owner, other_workspace)
