from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from itineraries.views import ItineraryViewSet, PublicItineraryViewSet

# Create a main router for the API root
router = DefaultRouter()
router.register(r"itineraries/my", ItineraryViewSet, basename="itinerary")
router.register(
    r"itineraries/public", PublicItineraryViewSet, basename="public-itinerary"
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/", include("users.urls")),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
