"""Settings index, all eight sections, and the team/data mutations."""
import json

import pytest
from django.urls import reverse

from apps.core.mock.store import SESSION_KEY

pytestmark = pytest.mark.django_db

SECTION_IDS = [
    "workspace",
    "monitoring",
    "notifications",
    "ai",
    "reports",
    "team",
    "data",
    "billing",
]


# ---------------------------------------------------------------------------
# Index + sections

def test_index_renders_workspace(client):
    response = client.get(reverse("settings_app:index"))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Settings" in html
    assert "Configure how RivalTracking works for your company." in html
    # Defaults to the workspace section.
    assert "Workspace name" in html


@pytest.mark.parametrize("section", SECTION_IDS)
def test_section_renders(client, section):
    response = client.get(reverse("settings_app:section", kwargs={"section": section}))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Settings" in html


def test_section_landmarks(client):
    team = client.get(reverse("settings_app:section", kwargs={"section": "team"})).content.decode()
    assert "Manage who can access this RivalTracking workspace." in team
    assert "Invite member" in team
    assert "Daniel Iancu" in team
    assert "Roles" in team

    data_html = client.get(reverse("settings_app:section", kwargs={"section": "data"})).content.decode()
    assert "Data &amp; Privacy" in data_html
    assert "Export data" in data_html
    assert "Danger zone" in data_html
    assert "Delete workspace" in data_html

    billing = client.get(reverse("settings_app:section", kwargs={"section": "billing"})).content.decode()
    assert "Manage your RivalTracking plan and usage." in billing
    assert "Manage plan" in billing
    assert "Usage" in billing
    assert "Growth" in billing


def test_unknown_section_falls_back_to_workspace(client):
    response = client.get(reverse("settings_app:section", kwargs={"section": "nope"}))
    assert response.status_code == 200
    assert "Workspace name" in response.content.decode()


# ---------------------------------------------------------------------------
# Mutations

def test_save_workspace(client):
    response = client.post(
        reverse("settings_app:save", kwargs={"section": "workspace"}),
        {
            "name": "Renamed Ltd",
            "website": "https://renamed.co.uk",
            "market": "United Kingdom",
            "industry": "Toys & Games",
            "currency": "GBP (£)",
            "timezone": "Europe/London",
            "date_format": "DD/MM/YYYY",
        },
    )
    assert response.status_code == 200
    assert "Settings saved" in response.content.decode()
    assert client.session[SESSION_KEY]["settings"]["workspace"]["name"] == "Renamed Ltd"


def test_team_invite_dialog_get(client):
    response = client.get(reverse("settings_app:team_invite"))
    assert response.status_code == 200
    assert "Invite member" in response.content.decode()


def test_team_invite_valid_email(client):
    response = client.post(
        reverse("settings_app:team_invite"),
        {"email": "new@acmetoys.co.uk", "role": "Analyst"},
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert "Invitation sent" in html
    team = client.session[SESSION_KEY]["settings"]["team"]
    assert any(m["email"] == "new@acmetoys.co.uk" and m["status"] == "Invited" for m in team)


def test_team_invite_invalid_email(client):
    response = client.post(
        reverse("settings_app:team_invite"), {"email": "not-an-email", "role": "Analyst"}
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert "Enter a valid email" in html


def test_data_delete_competitor(client):
    response = client.post(
        reverse("settings_app:data_delete_competitor"), {"competitor": "ToyWorld.co.uk"}
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert "Competitor data deleted" in html
    names = [c["name"] for c in client.session[SESSION_KEY]["competitors"]]
    assert "ToyWorld.co.uk" not in names


def test_data_delete_workspace_redirects(client):
    response = client.post(reverse("settings_app:data_delete_workspace"))
    assert response.status_code == 204
    assert response["HX-Redirect"] == "/"


def test_data_export_json_attachment(client):
    response = client.get(reverse("settings_app:data_export"))
    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    assert 'filename="rivaltracking-workspace.json"' in response["Content-Disposition"]
    payload = json.loads(response.content.decode())
    assert "workspace" in payload and "competitors" in payload
