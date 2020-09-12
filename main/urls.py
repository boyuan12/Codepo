from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new, name="new_repo"),
    path("profile/", views.edit_profile),
    path("follow/", views.follow_user),
    path("unfollow/", views.unfollow_user),
    path("create-oauth-app/", views.create_oauth_app),
    path("new-branch/", views.create_new_branch),
    path("<str:username>/", views.profile),
    path("<str:username>/<str:repo>/settings", views.repo_settings),
    path("<str:username>/<str:repo>/issues/", views.repo_issues),
    path("<str:username>/<str:repo>/issues/new/", views.repo_new_issue),
    path("<str:username>/<str:repo>/issues/<int:issue_id>", views.view_issue),
]