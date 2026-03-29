from rest_framework import serializers
from django.utils import timezone

from .models import Itinerary


class ItinerarySerializer(serializers.ModelSerializer):
    """Full serializer for itinerary owners - includes status field."""

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
        read_only_fields = ["id", "created_at", "updated_at", "suggested_status"]

    def get_suggested_status(self, obj):
        """Return the auto-calculated status based on dates."""
        return obj.get_auto_status()

    def validate(self, data):
        # For partial updates, we need to get the existing values
        if self.instance:
            start_date = data.get("start_date", self.instance.start_date)
            end_date = data.get("end_date", self.instance.end_date)
            old_status = self.instance.status
        else:
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            old_status = None

        # Validate dates
        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError("End date must be after start date")

            # Check trip duration (max 1 year)
            duration = (end_date - start_date).days
            if duration > 365:
                raise serializers.ValidationError(
                    "Trip duration cannot exceed 1 year"
                )

        # Validate status transitions
        new_status = data.get("status")
        if new_status and old_status:
            # Business rule: can't revert from completed to planning or ongoing
            if old_status == "completed" and new_status in ["planning", "ongoing"]:
                raise serializers.ValidationError(
                    "Cannot change status from completed back to planning or ongoing"
                )

        # Prevent creating trips with start date in the past (only for new trips)
        if not self.instance and start_date and start_date < timezone.now().date():
            raise serializers.ValidationError(
                "Cannot create itinerary with start date in the past"
            )

        # Validate activities
        activities = data.get("activities", [])
        if len(activities) > 100:
            raise serializers.ValidationError(
                "Maximum 100 activities allowed per itinerary"
            )

        return data


class PublicItinerarySerializer(serializers.ModelSerializer):
    """Public serializer - excludes status field."""

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
        read_only_fields = ["id", "created_at"]
