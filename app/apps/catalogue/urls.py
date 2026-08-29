from django.urls import path

from . import api

app_name = "catalogue"

urlpatterns = [
    path("api/ingest/", api.ingest, name="api_ingest"),
]
