from django.urls import path

from . import views

app_name = "ai"

urlpatterns = [
    path("", views.index, name="index"),
    path("ask/", views.ask, name="ask"),
    path("history-sheet/", views.history_sheet, name="history_sheet"),
    path("rename/", views.rename, name="rename"),
    path("delete/", views.delete, name="delete"),
]
