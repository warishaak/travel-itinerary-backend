from itineraries.api.serializers import (
    ItineraryReadSerializer,
    ItineraryWriteSerializer,
    PublicItineraryReadSerializer,
)

# Backward-compatible aliases for existing imports/tests.
ItinerarySerializer = ItineraryWriteSerializer
PublicItinerarySerializer = PublicItineraryReadSerializer

__all__ = [
    "ItineraryReadSerializer",
    "ItineraryWriteSerializer",
    "PublicItineraryReadSerializer",
    "ItinerarySerializer",
    "PublicItinerarySerializer",
]
