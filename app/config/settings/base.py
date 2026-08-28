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
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django_htmx",
    "apps.core",
    "apps.dashboard",
    "apps.competitors",
    "apps.products",
    "apps.changes",
    "apps.discovery",
    "apps.alerts",
    "apps.reports",
    "apps.ai",
    "apps.settings_app",
    "apps.accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
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
                "apps.core.context_processors.shell",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database sessions: the mock data store lives in the session and can exceed
# the 4KB signed-cookie limit, so cookie-based sessions must not be used.
SESSION_ENGINE = "django.contrib.sessions.backends.db"

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
