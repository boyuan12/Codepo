from django.urls import path
from . import views

urlpatterns = [
    path("delete/<str:username>/<str:repo>/", views.delete),
    path("visibility/<str:username>/<str:repo>/", views.change_repo_visibility),
    path("delete-repo/<str:username>/<str:repo>/", views.delete_repo),
    path("fork/<str:username>/<str:repo>/", views.fork),
    path("change-name/<str:username>/<str:repo>/", views.change_name),
    path("star/<str:username>/<str:repo>/", views.star),
    path("unstar/<str:username>/<str:repo>/", views.unstar),
    path("download_zip/<str:username>/<str:repo>/", views.download_zip),
    path("<str:username>/<str:repo>/upload/", views.upload),
    # path("<str:username>/<str:repo>/upload/<path:url>/", views.upload),
    path("<str:username>/<str:repo>/", views.repo),
    path("<str:username>/<str:repo>/edit/", views.edit),
    path("<str:username>/<str:repo>/<path:path>/", views.repo),
]