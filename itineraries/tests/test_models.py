"""
Unit tests for the Itinerary model.
"""

from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone

from itineraries.models import Itinerary


class ItineraryModelTest(TestCase):
    """Test suite for the Itinerary model"""

    def test_create_itinerary_with_valid_data(self):
        """Test creating an itinerary with all required fields"""
        itinerary_data = {
            "title": "Summer Vacation in Paris",
            "destination": "Paris, France",
            "start_date": date(2026, 7, 1),
            "end_date": date(2026, 7, 10),
        }

        itinerary = Itinerary.objects.create(**itinerary_data)

        self.assertIsNotNone(itinerary.id)
        self.assertEqual(itinerary.title, "Summer Vacation in Paris")
        self.assertEqual(itinerary.destination, "Paris, France")

    def test_itinerary_string_representation(self):
        """Test that __str__ returns the title"""
        itinerary = Itinerary.objects.create(
            title="Tokyo Adventure",
            destination="Tokyo, Japan",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
        )

        self.assertEqual(str(itinerary), "Tokyo Adventure")

    def test_timestamps_auto_populate(self):
        """Test that created_at and updated_at are set automatically"""
        before_creation = timezone.now()

        itinerary = Itinerary.objects.create(
            title="Test Trip",
            destination="Test Location",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
        )

        after_creation = timezone.now()
        self.assertIsNotNone(itinerary.created_at)
        self.assertGreaterEqual(itinerary.created_at, before_creation)
        self.assertLessEqual(itinerary.created_at, after_creation)
        self.assertIsNotNone(itinerary.updated_at)

    def test_default_ordering_by_created_at_desc(self):
        """Test that itineraries are ordered by creation date (newest first)"""
        itinerary1 = Itinerary.objects.create(
            title="First Trip",
            destination="Destination 1",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
        )
        import time

        time.sleep(0.01)

        itinerary2 = Itinerary.objects.create(
            title="Second Trip",
            destination="Destination 2",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
        )

        ordered_itineraries = list(Itinerary.objects.all())

        self.assertEqual(ordered_itineraries[0].id, itinerary2.id)
        self.assertEqual(ordered_itineraries[1].id, itinerary1.id)

    def test_field_constraints(self):
        """Test that model fields have correct constraints"""
        title_field = Itinerary._meta.get_field("title")
        destination_field = Itinerary._meta.get_field("destination")

        self.assertEqual(title_field.max_length, 200)
        self.assertEqual(destination_field.max_length, 200)
        self.assertFalse(title_field.blank)
