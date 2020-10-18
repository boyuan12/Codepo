from django.urls import path
from . import views

urlpatterns = [
    path("authorized/", views.authorize),
    path("access_token/", views.get_token),
    path("device_code/", views.get_device_code),
    path("device_code/verify/", views.device_code),
    path("device_code/access_token/", views.device_access_token),
    # path("a/", views.example),
]
