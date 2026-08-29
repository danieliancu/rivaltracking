from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required
from django.urls import path, reverse_lazy

from . import views

app_name = "accounts"


def _public(view):
    """Let anonymous users reach a built-in auth CBV under LoginRequiredMiddleware."""
    return login_not_required(view)


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("demo/", views.demo_login_view, name="demo_login"),
    path("logout/", views.logout_view, name="logout"),
    # Password reset flow (Django built-ins with themed templates).
    path(
        "password-reset/",
        _public(
            auth_views.PasswordResetView.as_view(
                template_name="accounts/password_reset.html",
                email_template_name="accounts/password_reset_email.html",
                subject_template_name="accounts/password_reset_subject.txt",
                success_url=reverse_lazy("accounts:password_reset_done"),
            )
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        _public(
            auth_views.PasswordResetDoneView.as_view(
                template_name="accounts/password_reset_done.html"
            )
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        _public(
            auth_views.PasswordResetConfirmView.as_view(
                template_name="accounts/password_reset_confirm.html",
                success_url=reverse_lazy("accounts:password_reset_complete"),
            )
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        _public(
            auth_views.PasswordResetCompleteView.as_view(
                template_name="accounts/password_reset_complete.html"
            )
        ),
        name="password_reset_complete",
    ),
]
