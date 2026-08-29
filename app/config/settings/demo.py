"""
Demo settings (Coolify): DEBUG off, WhiteNoise static files, one-click demo login.

Uses PostgreSQL when DB_HOST is provided (the Phase 2 target), otherwise falls
back to the Phase 1 SQLite file so the existing demo keeps working unchanged.
"""
from .base import *  # noqa: F401,F403
from .base import BASE_DIR, MIDDLEWARE, SQLITE_OPTIONS, env

DEBUG = False

SECRET_KEY = env("SECRET_KEY", required=True)

ALLOWED_HOSTS = [
    h.strip()
    for h in env("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in env("CSRF_TRUSTED_ORIGINS", default="").split(",")
    if o.strip()
]

if env("DB_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME", required=True),
            "USER": env("DB_USER", required=True),
            "PASSWORD": env("DB_PASSWORD", required=True),
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT", default="5432"),
            "CONN_MAX_AGE": int(env("DB_CONN_MAX_AGE", default="60")),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "OPTIONS": SQLITE_OPTIONS,
        }
    }

# Serve static files through WhiteNoise.
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# The demo intentionally offers the one-click "Enter the demo" sign-in.
DEMO_LOGIN_ENABLED = env("DEMO_LOGIN_ENABLED", default="1") not in ("0", "false", "False")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Phase 3: real Redis-backed cache (shared across web + workers) and real
# Celery workers (not eager). REDIS_URL / CELERY_* come from the environment.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("CACHE_URL", default=env("REDIS_URL", default="redis://localhost:6379/0")),
    }
}
CELERY_TASK_ALWAYS_EAGER = env("CELERY_TASK_ALWAYS_EAGER", default="0") not in ("0", "false", "False")

SCANNING_LIVE = env("SCANNING_LIVE", default="1") not in ("0", "false", "False")
