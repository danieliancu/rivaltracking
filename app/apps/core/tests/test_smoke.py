"""Every named page URL must render with a 200 and its landmark content.

This suite is the per-step "the app still runs" gate: each build step adds
its pages/fragments here.
"""
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

# (url_name, kwargs, landmark string expected in the response)
PAGES = [
    ("dashboard:overview", {}, "Overview"),
    ("competitors:index", {}, "Competitors"),
    ("competitors:detail", {"slug": "toyworld-co-uk"}, "Competitor"),
    ("products:index", {}, "Products"),
    ("products:detail", {"slug": "lego-castle-set"}, "Product"),
    ("changes:index", {}, "Changes"),
    ("discovery:index", {}, "Discovery"),
    ("alerts:index", {}, "Alerts"),
    ("reports:index", {}, "Reports"),
    ("reports:detail", {"report_id": "weekly-week-34"}, "Report"),
    ("ai:index", {}, "Ask AI"),
    ("settings_app:index", {}, "Settings"),
    ("settings_app:section", {"section": "billing"}, "Settings"),
]


@pytest.mark.parametrize("url_name,kwargs,landmark", PAGES)
def test_page_renders(client, url_name, kwargs, landmark):
    response = client.get(reverse(url_name, kwargs=kwargs))
    assert response.status_code == 200
    assert landmark in response.content.decode()


def test_custom_404(client):
    response = client.get("/no-such-page/really/")
    assert response.status_code == 404
