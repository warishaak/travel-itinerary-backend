from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from itineraries import views

router = routers.DefaultRouter()
router.register(r"itineraries", views.ItineraryViewSet, "itinerary")


urlpatterns = [
    path("", lambda request: HttpResponse("Welcome to Travel Itinerary API")),
    path("admin/", admin.site.urls),
    path("api/register/", views.RegisterView.as_view(), name="register"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include(router.urls)),
]
