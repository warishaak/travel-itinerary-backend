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
            "is_public",
            "activities",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        # For partial updates, we need to get the existing values
        if self.instance:
            start_date = data.get("start_date", self.instance.start_date)
            end_date = data.get("end_date", self.instance.end_date)
        else:
            start_date = data.get("start_date")
            end_date = data.get("end_date")

        # Only validate if both dates are present
        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError("End date must be after start date")

        return data
