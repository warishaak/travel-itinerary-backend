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
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        if data["end_date"] < data["start_date"]:
            raise serializers.ValidationError("End date must be after start date")
        return data
