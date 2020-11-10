from django.urls import path
from . import views

urlpatterns = [
    path("repo/", views.get_structure),
    path("create-directory/", views.create_directory),
    path("delete-directory/", views.delete_repository),
    path("modify-file/", views.modify_file),
    path("add-file/", views.add_file),
    path("delete-file/", views.delete_file),
    path("repos/", views.repos),
    path("sentry/", views.sentry_webhook),
    path("gen-commit/", views.gen_commit_id),
    path("file-data/", views.file_data),
    path("commit/", views.commit),
    path("user/", views.get_user_info),
    path("query-repo/", views.query_repo),
]