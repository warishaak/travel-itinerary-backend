from django.utils import timezone
from rest_framework import serializers

from itineraries.models import Itinerary


def validate_date_window(start_date, end_date, is_create):
    if start_date and end_date and end_date < start_date:
        raise serializers.ValidationError("End date must be after start date")

    if start_date and end_date:
        duration = (end_date - start_date).days
        if duration > 365:
            raise serializers.ValidationError("Trip duration cannot exceed 1 year")

    if is_create and start_date and start_date < timezone.now().date():
        raise serializers.ValidationError("Cannot create itinerary with start date in the past")


def validate_activities_limit(activities):
    if len(activities or []) > 100:
        raise serializers.ValidationError("Maximum 100 activities allowed per itinerary")


def validate_status_value(status):
    if status not in dict(Itinerary.STATUS_CHOICES):
        raise serializers.ValidationError("Invalid status")


def validate_status_transition(current_status, new_status):
    if current_status == "completed" and new_status in ["planning", "ongoing"]:
        raise serializers.ValidationError(
            "Cannot change status from completed back to planning or ongoing"
        )
