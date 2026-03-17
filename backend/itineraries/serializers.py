from rest_framework import serializers

from .models import Itinerary

class ItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = [
            "id",
            "title",
            "destination",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
        ]
