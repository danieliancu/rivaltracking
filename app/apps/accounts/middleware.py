"""Attach the active workspace to every authenticated request.

Runs after AuthenticationMiddleware and LoginRequiredMiddleware, so by the
time it sees a request the user is either anonymous (request.workspace stays
None) or authenticated. Views and selectors read ``request.workspace`` /
``request.membership`` to scope every query to the current tenant.
"""
from .selectors import resolve_active_workspace


class WorkspaceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.workspace = None
        request.membership = None
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            request.workspace, request.membership = resolve_active_workspace(request)
        return self.get_response(request)
