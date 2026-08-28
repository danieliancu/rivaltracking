from django.urls import path

from . import views

app_name = "changes"

urlpatterns = [
    path("", views.index, name="index"),
    path("export/", views.export, name="export"),
    path("ask-ai/", views.ask_ai, name="ask_ai"),
    path("create-alert/", views.create_alert, name="create_alert"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("<int:event_id>/drawer/", views.drawer, name="drawer"),
]
