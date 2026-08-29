"""Context shared by the application shell (sidebar + header) on every page."""
from django.urls import reverse


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

    from apps.alerts.models import Alert
    from apps.competitors import selectors as competitor_selectors

    workspace = getattr(request, "workspace", None)
    unread = Alert.objects.for_workspace(workspace).filter(
        status=Alert.Status.NEW
    ).count()
    competitors = competitor_selectors.header_list(request)
    scan_context = _scan_context(request)

    return {
        "nav_items": nav_items,
        "unread_count": unread,
        "ranges": RANGES,
        "date_range": request.session.get("date_range", "30d"),
        "header_competitors": competitors,
        "scan_context": scan_context,
        "daily_intelligence": _daily_intelligence(workspace),
        "catalogue_import": _catalogue_import(workspace),
        "current_workspace": workspace,
        "current_membership": getattr(request, "membership", None),
    }


def _daily_intelligence(workspace):
    """Today's change counts for the sidebar panel — real ChangeEvent data,
    all zero for a fresh workspace (never fabricated)."""
    from django.db.models import Count
    from django.utils import timezone

    from apps.changes.models import ChangeEvent

    today = timezone.localdate()
    counts = dict(
        ChangeEvent.objects.for_workspace(workspace)
        .filter(detected_at__date=today)
        .values_list("event_type")
        .annotate(n=Count("id"))
    )
    T = ChangeEvent.Type
    return [
        {"label": "New products", "value": counts.get(T.PRODUCT_NEW, 0)},
        {"label": "Price reductions", "value": counts.get(T.PRICE_DECREASE, 0)},
        {"label": "Now out of stock", "value": counts.get(T.STOCK_OUT, 0)},
        {"label": "New promotions", "value": counts.get(T.PROMOTION_STARTED, 0)},
    ]


def _catalogue_import(workspace):
    """Live website-import status for the header progress chip (None if the
    workspace has never connected a website source)."""
    from apps.catalogue.models import OwnCatalogueSource

    src = (
        OwnCatalogueSource.objects.filter(
            workspace=workspace,
            source_type=OwnCatalogueSource.SourceType.WEBSITE,
        )
        .only("status", "products_found", "domain", "website_url")
        .first()
    )
    if src is None:
        return None
    return {
        "status": src.status,
        "active": src.status == OwnCatalogueSource.Status.IMPORTING,
        "connected": src.status
        in (OwnCatalogueSource.Status.CONNECTED, OwnCatalogueSource.Status.PARTIAL),
        "count": src.products_found or 0,
        "domain": src.domain or src.website_url,
    }
