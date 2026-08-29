import json

from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from . import data, selectors, services


def _render_settings(request, active):
    context = {
        "sections": data.SETTINGS_SECTIONS,
        "active": active,
        "section_template": f"settings_app/partials/sections/{active}.html",
        **selectors.section_context(request, active),
    }
    return render(request, "settings_app/index.html", context)


def index(request):
    return _render_settings(request, "workspace")


def section(request, section):
    active = section if section in selectors.SECTION_IDS else "workspace"
    return _render_settings(request, active)


@require_POST
def save(request, section):
    """Save a settings section — workspace explicitly, the rest per control."""
    if section not in selectors.SECTION_IDS:
        raise Http404
    if section == "workspace":
        values, website_error = services.parse_workspace_post(request)
        if website_error:
            return render(
                request,
                "settings_app/partials/workspace_form.html",
                {
                    "w": values,
                    "options": data.WORKSPACE_OPTIONS,
                    "website_error": website_error,
                },
            )
        services.save_section(request, "workspace", values)
        return render(
            request,
            "settings_app/partials/workspace_save_response.html",
            {
                "w": selectors.settings_state(request)["workspace"],
                "options": data.WORKSPACE_OPTIONS,
                "saved": True,
            },
        )
    services.save_section(request, section, services.parse_autosave_post(request, section))
    return HttpResponse(status=204)


def _catalogue_dialog_context(request, **extra):
    from apps.catalogue import services as catalogue_services

    source = catalogue_services.get_source(request.workspace, "website")
    return {"website_source": source, **extra}


def _catalogue_dialog(request, **extra):
    return render(
        request,
        "settings_app/partials/connect_catalogue_dialog.html",
        _catalogue_dialog_context(request, **extra),
    )


def connect_catalogue(request):
    """Connect-your-catalogue dialog fragment (HTMX → #modal-root)."""
    return _catalogue_dialog(request)


@require_POST
def catalogue_connect(request):
    from apps.catalogue import services as catalogue_services

    source, error = catalogue_services.connect_website(
        request.workspace, request.POST.get("website_url", "")
    )
    return _catalogue_dialog(request, website_error=error)


@require_POST
def catalogue_rescan(request):
    from apps.catalogue import services as catalogue_services

    catalogue_services.rescan_website(request.workspace)
    return _catalogue_dialog(request)


@require_POST
def catalogue_disconnect(request):
    from apps.catalogue import services as catalogue_services

    catalogue_services.disconnect_source(request.workspace, "website")
    return _catalogue_dialog(request)


@require_POST
def catalogue_csv(request):
    from apps.catalogue import csv_import

    upload = request.FILES.get("file")
    result = None
    if upload is None:
        result = {"error": "Choose a CSV file to upload."}
    else:
        result = csv_import.import_csv(request.workspace, upload)
    return _catalogue_dialog(request, csv_result=result)


def manage_plan(request):
    """Manage-plan dialog fragment (HTMX → #modal-root)."""
    return render(request, "settings_app/partials/manage_plan_dialog.html")


# ---------------------------------------------------------------------------
# Team


def _team_response(request, toast):
    return render(
        request,
        "settings_app/partials/team_response.html",
        {
            "members": selectors.team_rows(request),
            "assignable_roles": selectors.ASSIGNABLE_ROLES,
            "toast": toast,
        },
    )


def team_invite(request):
    """GET: invite dialog fragment. POST: create the invited member."""
    if request.method != "POST":
        return render(
            request,
            "settings_app/partials/invite_dialog.html",
            {"roles": selectors.ASSIGNABLE_ROLES, "email": "", "role": "Member"},
        )
    email = request.POST.get("email", "").strip()
    role = request.POST.get("role", "Member")
    if not services.EMAIL_RE.match(email):
        return render(
            request,
            "settings_app/partials/invite_dialog.html",
            {
                "roles": selectors.ASSIGNABLE_ROLES,
                "email": email,
                "role": role,
                "email_error": "Enter a valid email",
            },
        )
    services.invite_member(request, email, role)
    return _team_response(
        request, {"variant": "success", "title": "Invitation sent", "description": email}
    )


@require_POST
def team_role(request, member_id):
    role = request.POST.get("role", "")
    if role not in selectors.ASSIGNABLE_ROLES:
        raise Http404
    member = services.change_role(request, member_id, role)
    if member is None:
        raise Http404
    return _team_response(
        request,
        {
            "variant": "success",
            "title": "Role updated",
            "description": f"{member['name']} is now {role}.",
        },
    )


@require_POST
def team_resend(request, member_id):
    """Resend an invitation — no store change, toast only."""
    member = selectors.member_by_id(request, member_id)
    if member is None:
        raise Http404
    return render(
        request,
        "partials/toast.html",
        {"variant": "success", "title": "Invitation resent", "description": member["email"]},
    )


def team_remove(request, member_id):
    """GET: remove-member confirm dialog. POST: remove the member."""
    member = selectors.member_by_id(request, member_id)
    if member is None:
        raise Http404
    if request.method != "POST":
        return render(
            request, "settings_app/partials/remove_member_dialog.html", {"member": member}
        )
    services.remove_member(request, member_id)
    return _team_response(
        request,
        {"variant": "info", "title": "Member removed", "description": member["email"]},
    )


# ---------------------------------------------------------------------------
# Data & Privacy


def data_export(request):
    """Download the workspace snapshot as JSON (lib/csv.ts downloadJson)."""
    payload = json.dumps(selectors.export_snapshot(request), indent=2)
    response = HttpResponse(payload, content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="rivaltracking-workspace.json"'
    return response


def data_delete_competitor(request):
    """GET: delete-competitor-data confirm dialog. POST: delete the data."""
    if request.method != "POST":
        return render(
            request,
            "settings_app/partials/delete_competitor_dialog.html",
            {"competitor_names": selectors.competitor_names(request)},
        )
    name = request.POST.get("competitor", "")
    services.delete_competitor_data(request, name)
    return render(
        request,
        "partials/toast.html",
        {
            "variant": "info",
            "title": "Competitor data deleted",
            "description": f"Historical data for {name} was removed.",
        },
    )


def data_delete_workspace(request):
    """GET: delete-workspace confirm dialog. POST: reset and redirect home."""
    if request.method != "POST":
        return render(
            request,
            "settings_app/partials/delete_workspace_dialog.html",
            {"workspace_name": selectors.settings_state(request)["workspace"]["name"]},
        )
    services.delete_workspace(request)
    response = HttpResponse(status=204)
    response["HX-Redirect"] = "/"
    return response
