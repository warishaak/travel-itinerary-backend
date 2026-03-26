from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"my", views.ItineraryViewSet, basename="itinerary")
router.register(r"public", views.PublicItineraryViewSet, basename="public-itinerary")

urlpatterns = [
    path("", include(router.urls)),
]
