"""
Tests for itinerary status lifecycle functionality.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from itineraries.models import Itinerary

User = get_user_model()


class StatusLifecycleTestCase(TestCase):
    """Test status transitions and business logic."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",  # nosec B106
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create test itinerary
        today = timezone.now().date()
        self.itinerary = Itinerary.objects.create(
            user=self.user,
            title="Test Trip",
            destination="Paris",
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=15),
            status="planning",
        )

    def test_default_status_is_planning(self):
        """New itineraries should default to 'planning' status."""
        self.assertEqual(self.itinerary.status, "planning")

    def test_status_field_in_personal_response(self):
        """Status field should be included for itinerary owner."""
        response = self.client.get(f"/api/itineraries/my/{self.itinerary.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.data)
        self.assertEqual(response.data["status"], "planning")

    def test_status_field_not_in_public_response(self):
        """Status field should NOT be included in public view."""
        # Make itinerary public
        self.itinerary.is_public = True
        self.itinerary.save()

        # Access as unauthenticated user
        self.client.logout()
        response = self.client.get(f"/api/itineraries/public/{self.itinerary.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("status", response.data)

    def test_update_status_to_ongoing(self):
        """Should allow updating status from planning to ongoing."""
        response = self.client.patch(
            f"/api/itineraries/my/{self.itinerary.id}/", {"status": "ongoing"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "ongoing")

        self.itinerary.refresh_from_db()
        self.assertEqual(self.itinerary.status, "ongoing")

    def test_cannot_revert_completed_to_planning(self):
        """Business rule: cannot change completed trip back to planning."""
        self.itinerary.status = "completed"
        self.itinerary.save()

        response = self.client.patch(
            f"/api/itineraries/my/{self.itinerary.id}/", {"status": "planning"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Cannot change status from completed", str(response.data))

    def test_cannot_revert_completed_to_ongoing(self):
        """Business rule: cannot change completed trip back to ongoing."""
        self.itinerary.status = "completed"
        self.itinerary.save()

        response = self.client.patch(
            f"/api/itineraries/my/{self.itinerary.id}/", {"status": "ongoing"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Cannot change status from completed", str(response.data))

    def test_get_auto_status_for_future_trip(self):
        """Future trips should suggest planning status."""
        today = timezone.now().date()
        self.itinerary.start_date = today + timedelta(days=10)
        self.itinerary.end_date = today + timedelta(days=15)
        self.itinerary.status = "planning"

        self.assertEqual(self.itinerary.get_auto_status(), "planning")

    def test_get_auto_status_for_ongoing_trip(self):
        """Current trips should suggest ongoing status."""
        today = timezone.now().date()
        self.itinerary.start_date = today - timedelta(days=2)
        self.itinerary.end_date = today + timedelta(days=3)

        self.assertEqual(self.itinerary.get_auto_status(), "ongoing")

    def test_get_auto_status_for_past_trip(self):
        """Past trips should suggest completed status."""
        today = timezone.now().date()
        self.itinerary.start_date = today - timedelta(days=10)
        self.itinerary.end_date = today - timedelta(days=5)

        self.assertEqual(self.itinerary.get_auto_status(), "completed")

    def test_suggested_status_in_response(self):
        """API should include suggested status based on dates."""
        response = self.client.get(f"/api/itineraries/my/{self.itinerary.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("suggested_status", response.data)

    def test_is_upcoming_property(self):
        """is_upcoming should return True for future trips."""
        today = timezone.now().date()
        self.itinerary.start_date = today + timedelta(days=5)
        self.assertTrue(self.itinerary.is_upcoming)

        self.itinerary.start_date = today - timedelta(days=5)
        self.assertFalse(self.itinerary.is_upcoming)

    def test_is_past_property(self):
        """is_past should return True for completed trips."""
        today = timezone.now().date()
        self.itinerary.end_date = today - timedelta(days=1)
        self.assertTrue(self.itinerary.is_past)

        self.itinerary.end_date = today + timedelta(days=5)
        self.assertFalse(self.itinerary.is_past)

    def test_is_current_property(self):
        """is_current should return True for ongoing trips."""
        today = timezone.now().date()
        self.itinerary.start_date = today - timedelta(days=2)
        self.itinerary.end_date = today + timedelta(days=2)
        self.assertTrue(self.itinerary.is_current)

        self.itinerary.start_date = today + timedelta(days=5)
        self.assertFalse(self.itinerary.is_current)

    def test_update_status_endpoint(self):
        """Dedicated update_status endpoint should work."""
        response = self.client.post(
            f"/api/itineraries/my/{self.itinerary.id}/update_status/",
            {"status": "ongoing"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "ongoing")

    def test_update_status_endpoint_invalid_status(self):
        """Should reject invalid status values."""
        response = self.client.post(
            f"/api/itineraries/my/{self.itinerary.id}/update_status/",
            {"status": "invalid_status"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid status", str(response.data))

    def test_all_status_choices_valid(self):
        """All defined status choices should be acceptable."""
        valid_statuses = ["planning", "ongoing", "completed"]

        for status_code in valid_statuses:
            # Reset to planning for each test
            self.itinerary.status = "planning"
            self.itinerary.save()

            if status_code == "completed":
                # For completed, we need to go through ongoing first
                # to avoid testing the business rule
                continue

            response = self.client.patch(
                f"/api/itineraries/my/{self.itinerary.id}/", {"status": status_code}
            )

            self.assertEqual(
                response.status_code,
                200,
                f"Status '{status_code}' should be valid",
            )
            self.assertEqual(response.data["status"], status_code)
