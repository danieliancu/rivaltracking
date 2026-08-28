from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.index, name="index"),
    path("export/", views.export_csv, name="export"),
    path("compare-selected/", views.compare_selected, name="compare_selected"),
    path("watchlist/add/", views.watchlist_add, name="watchlist_add"),
    path("<slug:slug>/", views.detail, name="detail"),
    path("<slug:slug>/compare/", views.compare_drawer, name="compare_drawer"),
    path("<slug:slug>/watchlist/", views.watchlist_toggle, name="watchlist_toggle"),
]
