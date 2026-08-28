from django.urls import path

from . import views

app_name = "discovery"

urlpatterns = [
    path("", views.index, name="index"),
    path("dialog/", views.dialog, name="dialog"),
    path("run/", views.run, name="run"),
    path("<slug:slug>/monitor/", views.monitor, name="monitor"),
    path("<slug:slug>/why-match/", views.why_match, name="why_match"),
    path("<slug:slug>/compare/", views.compare, name="compare"),
    path("<slug:slug>/not-relevant/", views.not_relevant, name="not_relevant"),
    path("<slug:slug>/dismiss/", views.dismiss, name="dismiss"),
]
