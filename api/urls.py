from django.urls import path
from . import views

urlpatterns = [
    path("repo/", views.get_structure)
]