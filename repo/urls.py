from django.urls import path
from . import views

urlpatterns = [
    path("<str:username>/<str:repo>/folder/", views.create_folder),
    path("<str:username>/<str:repo>/folder/<path:url>/", views.create_folder),
    path("<str:username>/<str:repo>/upload/", views.upload),
    path("<str:username>/<str:repo>/upload/<path:url>/", views.upload),
    path("<str:username>/<str:repo>/", views.repo),
    path("<str:username>/<str:repo>/<path:url>/", views.repo),
    path("visibility/<str:username>/<str:repo>/", views.change_repo_visibility),
    path("delete-repo/<str:username>/<str:repo>/", views.delete_repo),
]