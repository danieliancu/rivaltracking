from django.urls import path

from . import views

app_name = "settings_app"

urlpatterns = [
    path("", views.index, name="index"),
    # Fragment + mutation routes must precede the <slug:section> catch-all.
    path("save/<slug:section>/", views.save, name="save"),
    path("connect-catalogue/", views.connect_catalogue, name="connect_catalogue"),
    path("catalogue/connect/", views.catalogue_connect, name="catalogue_connect"),
    path("catalogue/rescan/", views.catalogue_rescan, name="catalogue_rescan"),
    path("catalogue/disconnect/", views.catalogue_disconnect, name="catalogue_disconnect"),
    path("catalogue/csv/", views.catalogue_csv, name="catalogue_csv"),
    path("manage-plan/", views.manage_plan, name="manage_plan"),
    path("team/invite/", views.team_invite, name="team_invite"),
    path("team/<str:member_id>/role/", views.team_role, name="team_role"),
    path("team/<str:member_id>/resend/", views.team_resend, name="team_resend"),
    path("team/<str:member_id>/remove/", views.team_remove, name="team_remove"),
    path("data/export/", views.data_export, name="data_export"),
    path("data/delete-competitor/", views.data_delete_competitor, name="data_delete_competitor"),
    path("data/delete-workspace/", views.data_delete_workspace, name="data_delete_workspace"),
    path("<slug:section>/", views.section, name="section"),
]
