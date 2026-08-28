from django.urls import path

from . import views

app_name = "competitors"

urlpatterns = [
    path("", views.index, name="index"),
    path("add/dialog/", views.add_dialog, name="add_dialog"),
    path("add/", views.add, name="add"),
    path("<slug:slug>/", views.detail, name="detail"),
    path("<slug:slug>/products/", views.products_fragment, name="products_fragment"),
    path("<slug:slug>/scan/", views.run_scan, name="run_scan"),
    path("<slug:slug>/pause/", views.pause_resume, name="pause_resume"),
    path("<slug:slug>/remove/", views.remove, name="remove"),
    path("<slug:slug>/monitoring/", views.monitoring_drawer, name="monitoring_drawer"),
    path("<slug:slug>/monitoring/save/", views.save_monitoring, name="save_monitoring"),
]
