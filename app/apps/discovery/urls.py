from django.urls import path

from . import views

app_name = "discovery"

urlpatterns = [
    path("", views.index, name="index"),
]
