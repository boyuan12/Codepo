from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new, name="new_repo"),
    path("profile/", views.edit_profile),
    path("follow/", views.follow_user),
    path("unfollow/", views.unfollow_user),
    path("create-oauth-app/", views.create_oauth_app),
    path("<str:username>/", views.profile),
]