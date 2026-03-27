from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Itinerary
from .serializers import ItinerarySerializer


class ItineraryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ItinerarySerializer

    def get_queryset(self):
        return Itinerary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicItineraryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = ItinerarySerializer

    def get_queryset(self):
        return Itinerary.objects.filter(is_public=True)
