"""A brand-new (non-seeded) workspace shows zero demo data everywhere."""
import pytest
from django.test import Client
from django.urls import reverse

from apps.accounts.selectors import ACTIVE_WORKSPACE_SESSION_KEY
from apps.accounts.services import register_account

pytestmark = pytest.mark.django_db

# Fabricated Phase 1 business data that must never appear for a real workspace.
FORBIDDEN = [
    "ToyWorld", "PlayNest", "HappyToyHouse", "LittleMinds", "BrightKidsPlay",
    "2,438", "8,746", "LEGO Castle Set", "Outdoor Toys pricing",
]

PAGES = [
    "/", "/competitors/", "/products/", "/changes/",
    "/discovery/", "/alerts/", "/reports/", "/ask-ai/", "/settings/",
]


@pytest.fixture
def empty_client(db):
    user, ws = register_account(email="fresh@demo.test", password="fresh-pass-12345", workspace_name="Fresh Co")
    client = Client(HTTP_HOST="localhost")
    client.force_login(user)
    session = client.session
    session[ACTIVE_WORKSPACE_SESSION_KEY] = ws.id
    session.save()
    client._workspace = ws
    return client


@pytest.mark.parametrize("path", PAGES)
def test_page_renders_with_no_demo_data(empty_client, path):
    response = empty_client.get(path)
    assert response.status_code == 200
    html = response.content.decode()
    for token in FORBIDDEN:
        assert token not in html, f"{token!r} leaked into {path}"


def test_empty_workspace_has_zero_records(empty_client):
    from apps.catalogue.models import Product, ProductListing
    from apps.changes.models import ChangeEvent
    from apps.competitors.models import Competitor

    ws = empty_client._workspace
    assert Competitor.objects.for_workspace(ws).count() == 0
    assert Product.objects.for_workspace(ws).count() == 0
    assert ProductListing.objects.for_workspace(ws).count() == 0
    assert ChangeEvent.objects.for_workspace(ws).count() == 0


def test_empty_workspace_kpis_and_empty_states(empty_client):
    products = empty_client.get(reverse("products:index")).content.decode()
    assert "No products available yet" in products
    changes = empty_client.get(reverse("changes:index")).content.decode()
    assert "Monitoring has started" in changes


def test_ask_ai_returns_no_data_on_empty_workspace(empty_client):
    response = empty_client.post(reverse("ai:ask"), {"question": "How are my competitors doing?"})
    assert response.status_code == 200
    html = response.content.decode()
    assert "Not enough data collected yet" in html
    for token in FORBIDDEN:
        assert token not in html


def test_reports_alerts_discovery_empty_states(empty_client):
    assert empty_client.get(reverse("reports:index")).status_code == 200
    assert empty_client.get(reverse("alerts:index")).status_code == 200
    discovery = empty_client.get(reverse("discovery:index")).content.decode()
    assert "No discoveries yet" in discovery
    assert "Add competitor by URL" in discovery
