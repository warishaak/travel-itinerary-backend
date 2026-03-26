from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("me/", views.CurrentUserView.as_view(), name="current_user"),
]
