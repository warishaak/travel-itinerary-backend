from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from itineraries.models import Itinerary

User = get_user_model()


class ItineraryAPITest(APITestCase):
    """Test suite for Itinerary API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com",
            username="owner@example.com",
            password="strongpass123",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            username="other@example.com",
            password="strongpass123",
        )

        self.itinerary1 = Itinerary.objects.create(
            user=self.user,
            title="Paris Vacation",
            destination="Paris, France",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 10),
        )
        self.itinerary2 = Itinerary.objects.create(
            user=self.other_user,
            title="Tokyo Adventure",
            destination="Tokyo, Japan",
            start_date=date(2026, 7, 15),
            end_date=date(2026, 7, 25),
        )

        self.my_list_url = reverse("itinerary-list")
        self.my_detail_url = lambda pk: reverse("itinerary-detail", kwargs={"pk": pk})
        self.public_list_url = reverse("public-itinerary-list")
        self.public_detail_url = lambda pk: reverse(
            "public-itinerary-detail", kwargs={"pk": pk}
        )

    def test_my_list_requires_authentication(self):
        response = self.client.get(self.my_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_list_returns_only_user_itineraries(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.my_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.itinerary1.id)

    def test_my_list_ordered_by_created_at_desc(self):
        self.client.force_authenticate(user=self.user)
        newest_itinerary = Itinerary.objects.create(
            user=self.user,
            title="Recent Trip",
            destination="London, UK",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
        )

        response = self.client.get(self.my_list_url)

        self.assertEqual(response.data[0]["id"], newest_itinerary.id)

    def test_create_itinerary_with_valid_data_returns_201(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "New York Trip",
            "destination": "New York City, USA",
            "start_date": "2026-08-01",
            "end_date": "2026-08-07",
        }

        response = self.client.post(self.my_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New York Trip")
        self.assertIn("id", response.data)
        self.assertIn("created_at", response.data)

    def test_create_itinerary_with_invalid_dates_returns_400(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Invalid Trip",
            "destination": "Boston, MA",
            "start_date": "2026-10-20",
            "end_date": "2026-10-15",
        }

        response = self.client.post(self.my_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_retrieve_own_itinerary_returns_200(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.my_detail_url(self.itinerary1.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.itinerary1.id)

    def test_retrieve_other_users_itinerary_returns_404(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.my_detail_url(self.itinerary2.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_itinerary_returns_200(self):
        self.client.force_authenticate(user=self.user)
        updated_data = {
            "title": "Updated Paris Trip",
            "destination": "Paris and Lyon, France",
            "start_date": "2026-06-05",
            "end_date": "2026-06-15",
        }

        response = self.client.put(
            self.my_detail_url(self.itinerary1.id), updated_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Paris Trip")

    def test_delete_itinerary_returns_204(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.my_detail_url(self.itinerary1.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Itinerary.objects.filter(id=self.itinerary1.id).exists())

    def test_public_list_returns_200(self):
        response = self.client.get(self.public_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_public_retrieve_returns_200(self):
        response = self.client.get(self.public_detail_url(self.itinerary1.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.itinerary1.id)

    def test_register_user_returns_201(self):
        data = {
            "email": "newuser@example.com",
            "password": "strongpass123",
            "password_confirm": "strongpass123",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post("/api/auth/register/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_token_obtain_returns_200(self):
        User.objects.create_user(
            email="loginuser@example.com",
            username="loginuser@example.com",
            password="strongpass123",
        )

        response = self.client.post(
            "/api/auth/token/",
            {"email": "loginuser@example.com", "password": "strongpass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
