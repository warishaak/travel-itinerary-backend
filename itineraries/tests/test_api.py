from datetime import date, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from itineraries.models import Itinerary


class ItineraryAPITest(APITestCase):
    """Test suite for Itinerary API endpoints"""

    def setUp(self):
        """Set up test data for each test"""
        self.itinerary1 = Itinerary.objects.create(
            title="Paris Vacation",
            destination="Paris, France",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 10),
        )
        self.itinerary2 = Itinerary.objects.create(
            title="Tokyo Adventure",
            destination="Tokyo, Japan",
            start_date=date(2026, 7, 15),
            end_date=date(2026, 7, 25),
        )

        self.list_url = reverse("itinerary-list")
        self.detail_url = lambda pk: reverse("itinerary-detail", kwargs={"pk": pk})

    def test_list_itineraries_returns_200(self):
        """Test GET /api/itineraries/ returns 200 OK"""
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_itineraries_ordered_by_created_at_desc(self):
        """Test that itineraries are returned in correct order (newest first)"""
        newest_itinerary = Itinerary.objects.create(
            title="Recent Trip",
            destination="London, UK",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.data[0]["id"], newest_itinerary.id)

    def test_create_itinerary_with_valid_data_returns_201(self):
        """Test POST /api/itineraries/ with valid data creates resource"""
        data = {
            "title": "New York Trip",
            "destination": "New York City, USA",
            "start_date": "2026-08-01",
            "end_date": "2026-08-07",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New York Trip")
        self.assertIn("id", response.data)
        self.assertIn("created_at", response.data)

    def test_create_itinerary_with_invalid_dates_returns_400(self):
        """Test that creating with end_date < start_date returns 400 Bad Request"""
        data = {
            "title": "Invalid Trip",
            "destination": "Boston, MA",
            "start_date": "2026-10-20",
            "end_date": "2026-10-15",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_create_itinerary_with_missing_fields_returns_400(self):
        """Test that missing required fields returns 400 Bad Request"""
        data = {
            "title": "Incomplete Trip",
            "start_date": "2026-11-01",
            "end_date": "2026-11-05",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("destination", response.data)

    def test_retrieve_itinerary_returns_200(self):
        """Test GET /api/itineraries/{id}/ returns 200 OK"""
        response = self.client.get(self.detail_url(self.itinerary1.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.itinerary1.id)
        self.assertEqual(response.data["title"], "Paris Vacation")

    def test_retrieve_nonexistent_itinerary_returns_404(self):
        """Test GET /api/itineraries/{id}/ with invalid ID returns 404"""
        response = self.client.get(self.detail_url(99999))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_itinerary_returns_200(self):
        """Test PUT /api/itineraries/{id}/ with valid data returns 200 OK"""
        updated_data = {
            "title": "Updated Paris Trip",
            "destination": "Paris and Lyon, France",
            "start_date": "2026-06-05",
            "end_date": "2026-06-15",
        }

        response = self.client.put(
            self.detail_url(self.itinerary1.id), updated_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Paris Trip")

    def test_partial_update_itinerary_returns_200(self):
        """Test PATCH /api/itineraries/{id}/ with partial data works"""
        partial_data = {"title": "Partially Updated Title"}

        response = self.client.patch(
            self.detail_url(self.itinerary2.id), partial_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Partially Updated Title")
        self.assertEqual(response.data["destination"], "Tokyo, Japan")

    def test_update_with_invalid_dates_returns_400(self):
        """Test that updating with invalid date range fails"""
        invalid_data = {
            "title": "Updated Trip",
            "destination": "Updated Destination",
            "start_date": "2026-08-20",
            "end_date": "2026-08-15",
        }

        response = self.client.put(
            self.detail_url(self.itinerary1.id), invalid_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_itinerary_returns_204(self):
        """Test DELETE /api/itineraries/{id}/ returns 204 No Content"""
        response = self.client.delete(self.detail_url(self.itinerary1.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Itinerary.objects.filter(id=self.itinerary1.id).exists())

    def test_delete_nonexistent_itinerary_returns_404(self):
        """Test deleting non-existent resource returns 404"""
        response = self.client.delete(self.detail_url(99999))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_register_user_returns_201(self):
        """Test POST /api/register/ creates a user."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "strongpass123",
        }

        response = self.client.post("/api/register/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_token_obtain_returns_200(self):
        """Test POST /api/token/ returns access and refresh tokens."""
        User.objects.create_user(
            username="loginuser",
            email="loginuser@example.com",
            password="strongpass123",
        )

        response = self.client.post(
            "/api/token/",
            {"username": "loginuser", "password": "strongpass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
