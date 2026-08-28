from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.index, name="index"),
    path("<slug:report_id>/", views.detail, name="detail"),
]
