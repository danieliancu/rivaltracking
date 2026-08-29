from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("", include("apps.dashboard.urls")),
    path("competitors/", include("apps.competitors.urls")),
    path("products/", include("apps.products.urls")),
    path("changes/", include("apps.changes.urls")),
    path("discovery/", include("apps.discovery.urls")),
    path("alerts/", include("apps.alerts.urls")),
    path("reports/", include("apps.reports.urls")),
    path("ask-ai/", include("apps.ai.urls")),
    path("settings/", include("apps.settings_app.urls")),
    path("", include("apps.core.urls")),
]

handler404 = "apps.core.views.not_found"
