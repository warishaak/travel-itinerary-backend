from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Itinerary
from .serializers import ItinerarySerializer, PublicItinerarySerializer


class ItineraryViewSet(viewsets.ModelViewSet):
    """Personal itineraries - full access including status."""

    permission_classes = [IsAuthenticated]
    serializer_class = ItinerarySerializer

    def get_queryset(self):
        return Itinerary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """
        Dedicated endpoint to update just the status field.
        Useful for quick status changes from the UI.
        """
        itinerary = self.get_object()
        new_status = request.data.get("status")

        if not new_status:
            return Response({"error": "Status is required"}, status=400)

        if new_status not in dict(Itinerary.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=400)

        # Use serializer for validation
        serializer = self.get_serializer(
            itinerary, data={"status": new_status}, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class PublicItineraryViewSet(viewsets.ReadOnlyModelViewSet):
    """Public itineraries - no status field visible."""

    permission_classes = [AllowAny]
    serializer_class = PublicItinerarySerializer

    def get_queryset(self):
        return Itinerary.objects.filter(is_public=True)
