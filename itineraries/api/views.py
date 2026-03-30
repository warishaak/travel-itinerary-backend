from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from itineraries.api.serializers import (
    ItineraryReadSerializer,
    ItineraryWriteSerializer,
    PublicItineraryReadSerializer,
    StatusUpdateInputSerializer,
)
from itineraries.permissions import IsItineraryOwnerPermission, PublicReadOnlyPermission
from itineraries.selectors.itinerary_selectors import (
    get_public_itineraries,
    get_user_itineraries,
)
from itineraries.services.status_service import ItineraryStatusService


class ItineraryViewSet(viewsets.ModelViewSet):
    """Owner itinerary endpoints with explicit read/write DTO serializers."""

    permission_classes = [IsItineraryOwnerPermission]

    def get_queryset(self):
        return get_user_itineraries(self.request.user)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve", "update_status"]:
            return ItineraryReadSerializer
        return ItineraryWriteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        new_status = serializer.validated_data.get("status")
        if new_status is not None:
            ItineraryStatusService.validate_transition(
                serializer.instance.status,
                new_status,
            )
        serializer.save()

    def create(self, request, *args, **kwargs):
        input_serializer = ItineraryWriteSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        itinerary = input_serializer.save(user=request.user)
        output_serializer = ItineraryReadSerializer(itinerary)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        itinerary = self.get_object()
        input_serializer = ItineraryWriteSerializer(
            itinerary,
            data=request.data,
            partial=partial,
        )
        input_serializer.is_valid(raise_exception=True)
        self.perform_update(input_serializer)
        output_serializer = ItineraryReadSerializer(itinerary)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        itinerary = self.get_object()
        input_serializer = StatusUpdateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        updated = ItineraryStatusService.update_status(
            itinerary=itinerary,
            new_status=input_serializer.validated_data["status"],
        )
        return Response(ItineraryReadSerializer(updated).data, status=status.HTTP_200_OK)


class PublicItineraryViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only itinerary endpoints."""

    permission_classes = [PublicReadOnlyPermission]
    serializer_class = PublicItineraryReadSerializer

    def get_queryset(self):
        return get_public_itineraries()
