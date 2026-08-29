"""Changes index page, HTMX fragments, drawer, export and watchlist."""
import pytest
from django.urls import reverse

from apps.changes.models import ChangeEvent

pytestmark = pytest.mark.django_db


def _event_id(workspace, slug="lego-castle-set"):
    return (
        ChangeEvent.objects.filter(workspace=workspace, product__slug=slug)
        .values_list("id", flat=True)
        .first()
    )


# ---------------------------------------------------------------------------
# Index page

def test_index_renders_landmarks(client):
    response = client.get(reverse("changes:index"))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Changes" in html
    assert "Track every meaningful change detected across your competitors." in html
    assert "AI Change Summary" in html
    assert "Major Change Patterns" in html
    assert "Change Events" in html
    assert "Change Activity" in html
    assert "Most Active Competitors" in html
    assert "LEGO Castle Set" in html
    # KPI row
    assert "Changes today" in html  # value is now ORM-derived


def test_index_filters_by_type(client):
    response = client.get(reverse("changes:index"), {"type": "price-decrease"})
    html = response.content.decode()
    assert response.status_code == 200
    assert "LEGO Castle Set" in html          # a price decrease (kind=drop)
    assert "STEM Robot Kit" not in html        # a promotion


def test_index_no_matches_empty_state(client):
    response = client.get(reverse("changes:index"), {"q": "zzz-no-such-thing"})
    html = response.content.decode()
    assert "No changes found" in html
    assert "Try adjusting your filters or selecting a wider date range." in html


# ---------------------------------------------------------------------------
# HTMX fragments

def test_events_fragment_returns_partial(client):
    response = client.get(
        reverse("changes:index"),
        {"type": "price-decrease"},
        HTTP_HX_REQUEST="true",
        HTTP_HX_TARGET="change-events",
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert "<html" not in html                 # partial only
    assert 'id="change-events"' in html
    assert "LEGO Castle Set" in html


def test_activity_fragment_returns_partial(client):
    response = client.get(
        reverse("changes:index"),
        {"activity": "price"},
        HTTP_HX_REQUEST="true",
        HTTP_HX_TARGET="change-activity",
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert "<html" not in html                 # partial only
    assert 'id="change-activity"' in html
    assert "Change Activity" in html


# ---------------------------------------------------------------------------
# Drawer

def test_drawer_fragment(client, workspace):
    response = client.get(reverse("changes:drawer", args=[_event_id(workspace)]))
    html = response.content.decode()
    assert response.status_code == 200
    assert "LEGO Castle Set" in html


def test_drawer_missing_event_404(client):
    response = client.get(reverse("changes:drawer", args=[999999]))
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Export

def test_export_csv(client):
    response = client.get(reverse("changes:export"))
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
    body = response.content.decode()
    assert "Change,Product,SKU,Competitor" in body
    assert "LEGO Castle Set" in body


def test_export_csv_ids_subset(client, workspace):
    response = client.get(reverse("changes:export"), {"ids": str(_event_id(workspace))})
    body = response.content.decode()
    assert "LEGO Castle Set" in body
    assert "Garden Water Table" not in body


# ---------------------------------------------------------------------------
# Watchlist mutation

def test_watchlist_post(client):
    response = client.post(reverse("changes:watchlist"), {"ids": "91824"})
    html = response.content.decode()
    assert response.status_code == 200
    assert "watchlist" in html
