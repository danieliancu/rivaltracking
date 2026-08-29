"""Context shared by the application shell (sidebar + header) on every page."""
from django.urls import reverse

from apps.core.store import WorkspaceStore

NAV = [
    ("Overview", "layout-dashboard", "dashboard:overview"),
    ("Competitors", "boxes", "competitors:index"),
    ("Products", "package", "products:index"),
    ("Changes", "git-compare-arrows", "changes:index"),
    ("Reports", "file-bar-chart-2", "reports:index"),
    ("Alerts", "bell", "alerts:index"),
    ("Ask AI", "sparkles", "ai:index"),
    ("Discovery", "compass", "discovery:index"),
    ("Settings", "settings", "settings_app:index"),
]

RANGES = [
    {"key": "today", "label": "Today"},
    {"key": "7d", "label": "7D"},
    {"key": "30d", "label": "30D"},
]


def _scan_context(request):
    """Competitor-detail route wins, then the dashboard competitor selector."""
    from apps.competitors import selectors as competitor_selectors

    match = request.resolver_match
    slug = None
    if match and match.namespace == "competitors" and match.url_name == "detail":
        slug = match.kwargs.get("slug")
    elif request.session.get("selected_competitor"):
        slug = request.session["selected_competitor"]
    if not slug:
        return None
    return competitor_selectors.name_for(request, slug)


def shell(request):
    user = getattr(request, "user", None)
    # Signed-out pages (login/signup/reset) render a standalone shell that does
    # not use any of this context, so keep it minimal and touch no tenant data.
    if user is None or not user.is_authenticated:
        return {"ranges": RANGES, "date_range": "30d"}

    path = request.path

    nav_items = []
    for label, icon, url_name in NAV:
        url = reverse(url_name)
        active = path == "/" if url == "/" else path.startswith(url)
        nav_items.append({"label": label, "icon": icon, "url": url, "active": active})

    from apps.competitors import selectors as competitor_selectors

    store = WorkspaceStore(request)
    try:
        recent_alerts = store.get("recent_alerts")
        unread = sum(1 for a in recent_alerts if a["status"] == "new")
    except (ImportError, KeyError):  # data modules land incrementally during the build
        unread = 0
    competitors = competitor_selectors.header_list(request)
    scan_context = _scan_context(request)

    return {
        "nav_items": nav_items,
        "unread_count": unread,
        "ranges": RANGES,
        "date_range": request.session.get("date_range", "30d"),
        "header_competitors": competitors,
        "scan_context": scan_context,
        "current_workspace": getattr(request, "workspace", None),
        "current_membership": getattr(request, "membership", None),
    }
