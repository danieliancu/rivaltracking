from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("dialogs/create/", views.create_dialog, name="create_dialog"),
    path("dialogs/schedule/", views.schedule_dialog, name="schedule_dialog"),
    path("fragments/generated/", views.generated_fragment, name="generated_fragment"),
    path("schedules/save/", views.save_schedule, name="save_schedule"),
    path("schedules/<slug:schedule_id>/toggle/", views.toggle_schedule, name="toggle_schedule"),
    path("schedules/<slug:schedule_id>/delete/", views.delete_schedule, name="delete_schedule"),
    path("<slug:report_id>/csv/", views.export_csv, name="export_csv"),
    path("<slug:report_id>/pdf/", views.download_pdf, name="download_pdf"),
    path("<slug:report_id>/regenerate/", views.regenerate, name="regenerate"),
    path("<slug:report_id>/delete/", views.delete, name="delete"),
    path("<slug:report_id>/", views.detail, name="detail"),
]
