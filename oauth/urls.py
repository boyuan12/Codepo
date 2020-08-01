
from django.urls import path
from . import views

urlpatterns = [
    path("authorized/", views.authorize),
    path("access_token/", views.get_token),
    # path("a/", views.example),
]