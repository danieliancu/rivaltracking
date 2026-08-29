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
    "apps.scanning",
    "apps.matching",
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


# ---------------------------------------------------------------------------
# Phase 3 — processing engine (Celery / Redis / scraping / AI)
# ---------------------------------------------------------------------------

REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")

# Celery. Eager mode (run tasks inline, no broker) is the default for local dev
# and tests; real deployments set CELERY_TASK_ALWAYS_EAGER=0 and run workers.
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default=REDIS_URL)
CELERY_TASK_ALWAYS_EAGER = env("CELERY_TASK_ALWAYS_EAGER", default="1") not in ("0", "false", "False")
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = int(env("CELERY_WORKER_PREFETCH_MULTIPLIER", default="1"))
CELERY_WORKER_CONCURRENCY = int(env("CELERY_WORKER_CONCURRENCY", default="4"))
CELERY_TASK_DEFAULT_QUEUE = "processing"
CELERY_TASK_TIME_LIMIT = int(env("CELERY_TASK_TIME_LIMIT", default="600"))
CELERY_TASK_SOFT_TIME_LIMIT = int(env("CELERY_TASK_SOFT_TIME_LIMIT", default="540"))
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 3600}
CELERY_RESULT_EXTENDED = True

# Route each kind of work to its own queue so heavy scraping/AI never starves
# lightweight processing. Workers subscribe to the queues they should serve.
CELERY_TASK_ROUTES = {
    "apps.scanning.tasks.*": {"queue": "scraping"},
    "apps.changes.tasks.*": {"queue": "processing"},
    "apps.catalogue.tasks.*": {"queue": "processing"},
    "apps.matching.tasks.*": {"queue": "matching"},
    "apps.ai.tasks.*": {"queue": "ai"},
    "apps.alerts.tasks.*": {"queue": "alerts"},
    "apps.reports.tasks.*": {"queue": "reports"},
}

# Beat: lightweight dispatchers (they enqueue real work, deduped via Redis locks).
CELERY_BEAT_SCHEDULE = {
    "dispatch-due-scans": {
        "task": "apps.scanning.tasks.dispatch_due_scans",
        "schedule": int(env("SCAN_DISPATCH_INTERVAL", default="60")),
    },
    "dispatch-due-report-schedules": {
        "task": "apps.reports.tasks.dispatch_due_schedules",
        "schedule": int(env("REPORT_DISPATCH_INTERVAL", default="300")),
    },
}

# Cache (also used for per-domain rate-limit leases and scan dedup locks).
# Local-memory by default so local dev and tests need no Redis; production and
# demo switch to a shared Redis cache (required for cross-worker locks).
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# Scraper controls (all overridable via env; conservative, resource-conscious).
HTTP_TIMEOUT = float(env("HTTP_TIMEOUT", default="15"))
HTTP_USER_AGENT = env(
    "HTTP_USER_AGENT",
    default="RivalTrackingBot/1.0 (+https://rivaltracking.com/bot)",
)
SCAN_MAX_PAGES = int(env("SCAN_MAX_PAGES", default="200"))
SCAN_MAX_DEPTH = int(env("SCAN_MAX_DEPTH", default="3"))
SCRAPER_CONCURRENCY = int(env("SCRAPER_CONCURRENCY", default="4"))
SCRAPER_PER_DOMAIN_RPS = float(env("SCRAPER_PER_DOMAIN_RPS", default="1"))
SCRAPER_MAX_RETRIES = int(env("SCRAPER_MAX_RETRIES", default="3"))
LISTING_MISSES_BEFORE_REMOVED = int(env("LISTING_MISSES_BEFORE_REMOVED", default="2"))
RAW_CAPTURE_RETENTION_DAYS = int(env("RAW_CAPTURE_RETENTION_DAYS", default="30"))

# Optional browser fetcher (Playwright). Off by default; needs the browser image.
BROWSER_ENABLED = env("BROWSER_ENABLED", default="0") in ("1", "true", "True")
BROWSER_CONCURRENCY = int(env("BROWSER_CONCURRENCY", default="1"))

# AI provider abstraction. Default "stub" is deterministic and needs no API key.
AI_PROVIDER = env("AI_PROVIDER", default="stub")
AI_MODEL = env("AI_MODEL", default="gpt-4o-mini")
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
AI_MAX_ANALYSES_PER_SCAN = int(env("AI_MAX_ANALYSES_PER_SCAN", default="30"))

# Live scanning hits real competitor sites; off locally/in tests (inject a
# fetcher instead), on in production/demo.
SCANNING_LIVE = env("SCANNING_LIVE", default="0") in ("1", "true", "True")
