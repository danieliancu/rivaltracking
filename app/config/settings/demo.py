from .base import *
from .base import env

DEBUG = False

SECRET_KEY = env("SECRET_KEY", required=True)

ALLOWED_HOSTS = [
    h.strip()
    for h in env(
        "ALLOWED_HOSTS",
        default="localhost,127.0.0.1"
    ).split(",")
    if h.strip()
]

# Phase 1 temporary demo: SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Serve static files through WhiteNoise
MIDDLEWARE.insert(
    1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True