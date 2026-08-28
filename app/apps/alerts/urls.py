from django.urls import path

from . import views

app_name = "alerts"

urlpatterns = [
    path("", views.index, name="index"),
    path("dialog/", views.rule_dialog, name="rule_dialog"),
    path("rules/create/", views.create_rule, name="create_rule"),
    path("rules/<str:rule_id>/update/", views.update_rule, name="update_rule"),
    path("rules/<str:rule_id>/toggle/", views.toggle_rule, name="toggle_rule"),
    path("rules/<str:rule_id>/duplicate/", views.duplicate_rule, name="duplicate_rule"),
    path("rules/<str:rule_id>/delete/", views.delete_rule, name="delete_rule"),
    path("notifications/<int:alert_id>/open/", views.open_alert, name="open_alert"),
    path("notifications/<int:alert_id>/read/", views.mark_read, name="mark_read"),
    path("notifications/read-all/", views.mark_all_read, name="mark_all_read"),
]
