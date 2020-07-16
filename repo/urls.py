from django.urls import path
from . import views

urlpatterns = [
    path("<str:username>/<str:repo>/upload/", views.upload),
    path("<str:username>/<str:repo>/upload/<path:url>", views.upload),
    path("<str:username>/<str:repo>/", views.repo),
    path("<str:username>/<str:repo>/<path:url>", views.repo)
]