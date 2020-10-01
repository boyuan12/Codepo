from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("logout/", views.logout_view, name="logout"),
    path("verify/<str:code>/", views.verify_account, name="verify account"),
    path("forgot-password/", views.forgot_password, name="forgot password"),
    path("forgot-password/<str:code>/", views.reset_password, name="reset password")
]