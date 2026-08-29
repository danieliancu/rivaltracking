"""Local development settings: SQLite, DEBUG on, permissive defaults."""
from .base import *  # noqa: F401,F403
from .base import BASE_DIR, SQLITE_OPTIONS, env

DEBUG = True

SECRET_KEY = env("SECRET_KEY", default="dev-only-insecure-secret-key")

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": SQLITE_OPTIONS,
    }
}
