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
        self.itinerary1.is_public = True
        self.itinerary1.save()
        self.itinerary2.is_public = True
        self.itinerary2.save()

        response = self.client.get(self.public_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_public_retrieve_returns_200(self):
        self.itinerary1.is_public = True
        self.itinerary1.save()

        response = self.client.get(self.public_detail_url(self.itinerary1.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.itinerary1.id)

    def test_partial_update_itinerary_returns_200(self):
        self.client.force_authenticate(user=self.user)
        patch_data = {"title": "Updated Title Only"}

        response = self.client.patch(
            self.my_detail_url(self.itinerary1.id), patch_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Title Only")
        self.assertEqual(response.data["destination"], "Paris, France")

    def test_create_itinerary_with_activities_returns_201(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Activity Test Trip",
            "destination": "London, UK",
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
            "activities": [
                {"name": "Visit Tower of London", "day": 1},
                {"name": "British Museum", "day": 2},
            ],
        }

        response = self.client.post(self.my_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["activities"]), 2)
        self.assertEqual(
            response.data["activities"][0]["name"], "Visit Tower of London"
        )

    def test_create_itinerary_assigns_user_automatically(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "User Assignment Test",
            "destination": "Berlin, Germany",
            "start_date": "2026-10-01",
            "end_date": "2026-10-05",
        }

        response = self.client.post(self.my_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_itinerary = Itinerary.objects.get(id=response.data["id"])
        self.assertEqual(created_itinerary.user, self.user)

    def test_create_public_itinerary_returns_201(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Public Trip",
            "destination": "Rome, Italy",
            "start_date": "2026-11-01",
            "end_date": "2026-11-07",
            "is_public": True,
        }

        response = self.client.post(self.my_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["is_public"])

    def test_public_list_excludes_private_itineraries(self):
        self.itinerary1.is_public = True
        self.itinerary1.save()

        response = self.client.get(self.public_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.itinerary1.id)

    def test_private_itinerary_not_accessible_via_public_endpoint(self):
        response = self.client.get(self.public_detail_url(self.itinerary1.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_itinerary_activities_returns_200(self):
        self.client.force_authenticate(user=self.user)
        updated_activities = [
            {"name": "Eiffel Tower", "time": "10:00 AM"},
            {"name": "Louvre Museum", "time": "2:00 PM"},
            {"name": "Seine River Cruise", "time": "7:00 PM"},
        ]
        patch_data = {"activities": updated_activities}

        response = self.client.patch(
            self.my_detail_url(self.itinerary1.id), patch_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["activities"]), 3)
        self.assertEqual(response.data["activities"][0]["name"], "Eiffel Tower")

    def test_update_is_public_field_returns_200(self):
        self.client.force_authenticate(user=self.user)
        self.assertFalse(self.itinerary1.is_public)

        response = self.client.patch(
            self.my_detail_url(self.itinerary1.id), {"is_public": True}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_public"])
        self.itinerary1.refresh_from_db()
        self.assertTrue(self.itinerary1.is_public)

    def test_cannot_create_itinerary_without_authentication(self):
        data = {
            "title": "Unauthorized Trip",
            "destination": "Somewhere",
            "start_date": "2026-12-01",
            "end_date": "2026-12-05",
        }

        response = self.client.post(self.my_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_update_other_users_itinerary(self):
        self.client.force_authenticate(user=self.user)
        patch_data = {"title": "Hacked Title"}

        response = self.client.patch(
            self.my_detail_url(self.itinerary2.id), patch_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.itinerary2.refresh_from_db()
        self.assertEqual(self.itinerary2.title, "Tokyo Adventure")

    def test_cannot_delete_other_users_itinerary(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.my_detail_url(self.itinerary2.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Itinerary.objects.filter(id=self.itinerary2.id).exists())
