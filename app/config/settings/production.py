"""
Production settings: PostgreSQL, env-provided secrets.

NOTE: Phase 1 ships no production deployment. This module exists so the
project is PostgreSQL-ready from day one; static file serving (e.g.
whitenoise) and hardening are part of a later phase.
"""
from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

SECRET_KEY = env("SECRET_KEY", required=True)

ALLOWED_HOSTS = [h for h in env("ALLOWED_HOSTS", default="").split(",") if h]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", required=True),
        "USER": env("DB_USER", required=True),
        "PASSWORD": env("DB_PASSWORD", required=True),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    }
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
