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

    def test_default_is_public_is_false(self):
        """Test that is_public defaults to False"""
        itinerary = Itinerary.objects.create(
            title="Private Trip",
            destination="Secret Location",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
        )

        self.assertFalse(itinerary.is_public)

    def test_activities_field_defaults_to_empty_list(self):
        """Test that activities field defaults to empty list"""
        itinerary = Itinerary.objects.create(
            title="No Activities Trip",
            destination="Somewhere",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
        )

        self.assertEqual(itinerary.activities, [])

    def test_activities_field_stores_json_data(self):
        """Test that activities field can store JSON data"""
        activities_data = [
            {"name": "Activity 1", "time": "10:00 AM", "location": "Place A"},
            {"name": "Activity 2", "time": "2:00 PM", "location": "Place B"},
        ]
        itinerary = Itinerary.objects.create(
            title="Activities Trip",
            destination="Test City",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            activities=activities_data,
        )

        self.assertEqual(len(itinerary.activities), 2)
        self.assertEqual(itinerary.activities[0]["name"], "Activity 1")
        self.assertEqual(itinerary.activities[1]["location"], "Place B")

    def test_user_field_can_be_null(self):
        """Test that user field can be null"""
        itinerary = Itinerary.objects.create(
            user=None,
            title="No User Trip",
            destination="Anywhere",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
        )

        self.assertIsNone(itinerary.user)

    def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when itinerary is saved"""
        itinerary = Itinerary.objects.create(
            title="Update Test",
            destination="Test Location",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
        )
        original_updated_at = itinerary.updated_at

        import time
        time.sleep(0.01)

        itinerary.title = "Updated Title"
        itinerary.save()

        self.assertGreater(itinerary.updated_at, original_updated_at)
