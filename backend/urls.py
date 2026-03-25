from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from rest_framework import routers

from itineraries import views

router = routers.DefaultRouter()
router.register(r"itineraries", views.ItineraryViewSet, "itinerary")


urlpatterns = [
    path("", lambda request: HttpResponse("Welcome to Travel Itinerary API")),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
