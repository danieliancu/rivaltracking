"""Read helpers for identity/tenancy: memberships and active-workspace resolution."""
from .models import WorkspaceMembership

ACTIVE_WORKSPACE_SESSION_KEY = "active_workspace_id"


def memberships_for(user):
    """All memberships for a user, workspace prefetched, stable order."""
    return (
        WorkspaceMembership.objects.filter(user=user)
        .select_related("workspace")
        .order_by("workspace__name")
    )


def membership_in(user, workspace):
    """The user's membership in a workspace, or None."""
    if user is None or not user.is_authenticated or workspace is None:
        return None
    return (
        WorkspaceMembership.objects.filter(user=user, workspace=workspace)
        .select_related("workspace")
        .first()
    )


def resolve_active_workspace(request):
    """Return (workspace, membership) for the request's user.

    Honours the session's active-workspace choice when the user still belongs
    to it, otherwise falls back to their first membership. Returns (None, None)
    when the user has no memberships.
    """
    user = request.user
    memberships = list(memberships_for(user))
    if not memberships:
        return None, None

    chosen_id = request.session.get(ACTIVE_WORKSPACE_SESSION_KEY)
    membership = None
    if chosen_id is not None:
        membership = next(
            (m for m in memberships if m.workspace_id == chosen_id), None
        )
    if membership is None:
        membership = memberships[0]
        request.session[ACTIVE_WORKSPACE_SESSION_KEY] = membership.workspace_id

    return membership.workspace, membership
