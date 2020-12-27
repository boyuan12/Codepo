from django.urls import path
from . import views

urlpatterns = [
    path("authenticate/", views.github_auth),
    path("callback/", views.github_callback),
    path("create-repo/<str:username>/<str:repo>/", views.create_repo),
    path("sync-repo/", views.sync_repo),
]