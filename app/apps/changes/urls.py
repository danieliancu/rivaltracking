from django.urls import path

from . import views

app_name = "changes"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:event_id>/drawer/", views.drawer, name="drawer"),
]
