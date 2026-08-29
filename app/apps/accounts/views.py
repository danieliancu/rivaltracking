"""Authentication views: login, signup, logout, demo entry.

All views here opt out of the global LoginRequiredMiddleware via
@login_not_required so anonymous visitors can reach them.
"""
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LoginForm, SignupForm
from .models import User
from .services import register_account


def _safe_next(request, fallback_name="dashboard:overview"):
    nxt = request.POST.get("next") or request.GET.get("next")
    if nxt and url_has_allowed_host_and_scheme(
        nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return nxt
    return reverse(fallback_name)


@login_not_required
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:overview")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(_safe_next(request))
    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "next": request.GET.get("next", ""),
            "demo_enabled": settings.DEMO_LOGIN_ENABLED,
            "demo_email": settings.DEMO_EMAIL,
        },
    )


@login_not_required
@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:overview")
    form = SignupForm(data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user, _ = register_account(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password2"],
            first_name=form.cleaned_data.get("first_name", ""),
            last_name=form.cleaned_data.get("last_name", ""),
            workspace_name=form.cleaned_data.get("workspace_name", ""),
        )
        authenticated = authenticate(
            request, email=user.email, password=form.cleaned_data["password2"]
        )
        login(request, authenticated)
        return redirect("dashboard:overview")
    return render(request, "accounts/signup.html", {"form": form})


@login_not_required
@require_POST
def demo_login_view(request):
    """One-click, password-less sign-in of the seeded demo user.

    Deliberate public-demo bypass, gated by DEMO_LOGIN_ENABLED — there is no
    demo password anywhere in the codebase.
    """
    if not settings.DEMO_LOGIN_ENABLED:
        return redirect("accounts:login")
    user = User.objects.filter(email__iexact=settings.DEMO_EMAIL).first()
    if user is None:
        return render(
            request,
            "accounts/login.html",
            {
                "form": LoginForm(request),
                "demo_enabled": True,
                "demo_email": settings.DEMO_EMAIL,
                "demo_error": "Demo account is not available. Run `manage.py seed_demo`.",
            },
        )
    login(request, user, backend="apps.accounts.backends.EmailBackend")
    return redirect("dashboard:overview")


@require_POST
def logout_view(request):
    logout(request)
    return redirect("accounts:login")
