"""
Base settings shared by all environments.

Environment-specific values come from environment variables via env().
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class ImproperlyConfiguredEnv(Exception):
    pass


def env(name, default=None, required=False):
    """Read a configuration value from the environment."""
    value = os.environ.get(name, default)
    if required and value in (None, ""):
        raise ImproperlyConfiguredEnv(f"Required environment variable {name} is not set.")
    return value


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_htmx",
    "apps.core",
    "apps.accounts",
    "apps.catalogue",
    "apps.dashboard",
    "apps.competitors",
    "apps.products",
    "apps.changes",
    "apps.discovery",
    "apps.alerts",
    "apps.reports",
    "apps.ai",
    "apps.settings_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    # Requires authentication for every view unless it opts out via the
    # @login_not_required decorator (auth pages do). Must run after
    # AuthenticationMiddleware so request.user is populated.
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    # Resolves request.workspace from the authenticated user's membership.
    # Must run after LoginRequiredMiddleware so it only sees signed-in users.
    "apps.accounts.middleware.WorkspaceMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": False,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.shell",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database-backed sessions. Kept from Phase 1 (the shell stores lightweight
# per-request state such as the active date range and workspace here).
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Authentication ---------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = ["apps.accounts.backends.EmailBackend"]
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:overview"
LOGOUT_REDIRECT_URL = "accounts:login"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Email: console backend by default (password-reset links print to the log).
# Wire a real SMTP backend via env in a later phase.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL", default="RivalTracking <no-reply@rivaltracking.com>"
)

# One-click demo sign-in on the login page. The demo user is created by
# `manage.py seed_demo`; disable in real production deployments.
DEMO_LOGIN_ENABLED = env("DEMO_LOGIN_ENABLED", default="1") not in ("0", "false", "False")
DEMO_EMAIL = env("DEMO_EMAIL", default="demo@rivaltracking.com")
DEMO_PASSWORD = env("DEMO_PASSWORD", default="demo-rivaltracking")

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
