"""
Tests for the ItinerarySerializer validation logic.
"""

from datetime import date

from django.test import TestCase

from itineraries.models import Itinerary
from itineraries.serializers import ItinerarySerializer


class ItinerarySerializerTest(TestCase):
    """Test suite for the ItinerarySerializer validation logic"""

    def test_valid_itinerary_serialization(self):
        """Test serializing valid itinerary data"""
        valid_data = {
            "title": "Weekend Getaway",
            "destination": "New York City",
            "start_date": "2026-08-01",
            "end_date": "2026-08-03",
        }

        serializer = ItinerarySerializer(data=valid_data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["title"], "Weekend Getaway")

    def test_end_date_equal_to_start_date_is_valid(self):
        """Test that single-day itineraries (same start/end) are valid"""
        same_day = "2026-10-15"
        data = {
            "title": "Day Trip",
            "destination": "San Francisco",
            "start_date": same_day,
            "end_date": same_day,
        }

        serializer = ItinerarySerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_end_date_before_start_date_raises_error(self):
        """Test that end_date before start_date fails validation"""
        data = {
            "title": "Invalid Trip",
            "destination": "Chicago",
            "start_date": "2026-11-10",
            "end_date": "2026-11-05",
        }

        serializer = ItinerarySerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(
            str(serializer.errors["non_field_errors"][0]),
            "End date must be after start date",
        )

    def test_read_only_fields_cannot_be_set(self):
        """Test that ID and created_at cannot be manually set"""
        data = {
            "id": 999,
            "title": "Test Trip",
            "destination": "Test Location",
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
            "created_at": "2020-01-01T00:00:00Z",
        }

        serializer = ItinerarySerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertNotIn("id", serializer.validated_data)
        self.assertNotIn("created_at", serializer.validated_data)

    def test_required_fields_validation(self):
        """Test validation error when required fields are missing"""
        data = {
            "title": "Incomplete Trip",
            "start_date": "2026-08-01",
            "end_date": "2026-08-05",
        }

        serializer = ItinerarySerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("destination", serializer.errors)

    def test_partial_update_validation(self):
        """Test that partial updates still enforce date validation"""
        itinerary = Itinerary.objects.create(
            title="Original Trip",
            destination="Portland",
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 10),
        )

        invalid_update = {"end_date": "2026-09-25"}
        serializer = ItinerarySerializer(itinerary, data=invalid_update, partial=True)

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
