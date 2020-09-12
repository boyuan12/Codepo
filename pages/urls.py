
from django.urls import path
from . import views

urlpatterns = [
    path("<str:username>/<str:repo>/", views.index),
    path("<str:username>/<str:repo>/<path:path>/", views.index),
]