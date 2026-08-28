from django.urls import path

from . import views

app_name = "settings_app"

urlpatterns = [
    path("", views.index, name="index"),
    path("<slug:section>/", views.section, name="section"),
]
