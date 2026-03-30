from rest_framework import serializers

from itineraries.domain.rules import (
    validate_activities_limit,
    validate_date_window,
    validate_status_value,
)
from itineraries.models import Itinerary


class ItineraryWriteSerializer(serializers.ModelSerializer):
    """Input DTO for owner itinerary create/update operations."""

    class Meta:
        model = Itinerary
        fields = [
            "id",
            "title",
            "destination",
            "start_date",
            "end_date",
            "is_public",
            "status",
            "activities",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        if self.instance:
            start_date = data.get("start_date", self.instance.start_date)
            end_date = data.get("end_date", self.instance.end_date)
            is_create = False
            activities = data.get("activities", self.instance.activities)
        else:
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            is_create = True
            activities = data.get("activities", [])

        validate_date_window(start_date, end_date, is_create=is_create)
        validate_activities_limit(activities)
        return data


class ItineraryReadSerializer(serializers.ModelSerializer):
    """Output DTO for owner itinerary reads."""

    suggested_status = serializers.SerializerMethodField()

    class Meta:
        model = Itinerary
        fields = [
            "id",
            "title",
            "destination",
            "start_date",
            "end_date",
            "is_public",
            "status",
            "suggested_status",
            "activities",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_suggested_status(self, obj):
        return obj.get_auto_status()


class PublicItineraryReadSerializer(serializers.ModelSerializer):
    """Output DTO for public itinerary reads."""

    class Meta:
        model = Itinerary
        fields = [
            "id",
            "title",
            "destination",
            "start_date",
            "end_date",
            "activities",
            "images",
            "created_at",
        ]
        read_only_fields = fields


class StatusUpdateInputSerializer(serializers.Serializer):
    """Input DTO for dedicated status updates."""

    status = serializers.CharField(max_length=20)

    def validate_status(self, value):
        validate_status_value(value)
        return value
