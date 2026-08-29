from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("search/", views.search, name="search"),
    path("range/", views.set_range, name="set_range"),
    path("scan/", views.run_scan, name="run_scan"),
    path("scan-status/", views.scan_status, name="scan_status"),
    path("sign-out/", views.sign_out, name="sign_out"),
    path("dev/reset/", views.reset_demo, name="reset_demo"),
    path("dev/404/", views.not_found_preview, name="not_found_preview"),
]
