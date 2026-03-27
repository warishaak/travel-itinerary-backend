from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("me/", views.CurrentUserView.as_view(), name="current_user"),
    path(
        "password-reset/request/",
        views.RequestPasswordResetView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password-reset/confirm/",
        views.ConfirmPasswordResetView.as_view(),
        name="password_reset_confirm",
    ),
]
