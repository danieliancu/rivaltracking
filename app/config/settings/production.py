"""
Production settings: PostgreSQL, env-provided secrets, WhiteNoise static files.

All required secrets come from environment variables (see .env.example and the
README's Coolify section). No Redis/Celery yet — that is Phase 3.
"""
from .base import *  # noqa: F401,F403
from .base import MIDDLEWARE, env

DEBUG = False

SECRET_KEY = env("SECRET_KEY", required=True)

ALLOWED_HOSTS = [h for h in env("ALLOWED_HOSTS", default="").split(",") if h]

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in env("CSRF_TRUSTED_ORIGINS", default="").split(",")
    if o.strip()
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", required=True),
        "USER": env("DB_USER", required=True),
        "PASSWORD": env("DB_PASSWORD", required=True),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
        "CONN_MAX_AGE": int(env("DB_CONN_MAX_AGE", default="60")),
    }
}

# Serve static files through WhiteNoise (no separate static server needed).
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Real deployments disable the one-click demo sign-in unless explicitly enabled.
DEMO_LOGIN_ENABLED = env("DEMO_LOGIN_ENABLED", default="0") not in ("0", "false", "False")

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
