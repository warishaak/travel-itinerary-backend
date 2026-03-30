from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import PasswordReset

from . import get_authenticated_client
from .test_factories import UserFactory

User = get_user_model()


class UserRegistrationAPITest(APITestCase):
    """Integration tests for user registration API endpoint."""

    def setUp(self):
        cache.clear()
        self.register_url = reverse("register")

    def test_register_with_valid_data_returns_201(self):
        """Test successful registration returns 201 Created."""
        data = UserFactory.build_registration_data()
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("email", response.data)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "User created successfully")

    def test_register_creates_user_in_database(self):
        """Test registration creates user in database."""
        data = UserFactory.build_registration_data(email="dbuser@example.com")
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="dbuser@example.com").exists())

        user = User.objects.get(email="dbuser@example.com")
        self.assertEqual(user.email, "dbuser@example.com")
        self.assertEqual(user.username, "dbuser@example.com")

    def test_register_hashes_password_not_plain_text(self):
        """Test password is hashed, not stored as plain text."""
        data = UserFactory.build_registration_data(
            email="hashtest@example.com",
            password="TestPass123!",
            password_confirm="TestPass123!",
        )
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="hashtest@example.com")
        self.assertNotEqual(user.password, "TestPass123!")
        self.assertTrue(user.check_password("TestPass123!"))

    def test_register_with_duplicate_email_returns_400(self):
        """Test registration with duplicate email returns 400 Bad Request."""
        existing_user = UserFactory.create_user(email="duplicate@example.com")
        data = UserFactory.build_duplicate_email_data(existing_user)
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_with_password_mismatch_returns_400(self):
        """Test registration with password mismatch returns 400."""
        data = UserFactory.build_password_mismatch_data()
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)

    def test_register_with_weak_password_returns_400(self):
        """Test registration with weak password returns 400."""
        weak_passwords = UserFactory.build_weak_password_data()

        for data in weak_passwords:
            response = self.client.post(self.register_url, data)
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f"Weak password {data['password']} should fail",
            )
            self.assertIn("password", response.data)

    def test_register_with_missing_required_fields_returns_400(self):
        """Test registration without required fields returns 400."""
        test_cases = [
            {},
            {"email": "test@example.com"},
            {"password": "TestPass123!", "password_confirm": "TestPass123!"},
        ]

        for data in test_cases:
            response = self.client.post(self.register_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_invalid_email_format_returns_400(self):
        """Test registration with invalid email format returns 400."""
        data = UserFactory.build_invalid_email_data()
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_response_does_not_include_password(self):
        """Test registration response does not expose password."""
        data = UserFactory.build_registration_data()
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)
        self.assertNotIn("password_confirm", response.data)

    def test_register_endpoint_allows_unauthenticated_access(self):
        """Test registration endpoint is public."""
        data = UserFactory.build_registration_data()
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CurrentUserAPITest(APITestCase):
    """Integration tests for current user (/me/) API endpoint."""

    def setUp(self):
        self.user = UserFactory.create_user(
            email="currentuser@example.com",
            password="TestPass123!",
            first_name="Current",
            last_name="User",
        )
        self.me_url = reverse("current_user")

    def test_get_current_user_requires_authentication(self):
        """Test GET /me/ without authentication returns 401."""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_current_user_returns_user_data(self):
        """Test GET /me/ returns authenticated user's data."""
        client = get_authenticated_client(self.user)
        response = client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("email", response.data)
        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)
        self.assertEqual(response.data["email"], "currentuser@example.com")
        self.assertEqual(response.data["first_name"], "Current")
        self.assertEqual(response.data["last_name"], "User")

    def test_get_current_user_returns_correct_user(self):
        """Test GET /me/ returns only authenticated user's data."""
        user1 = UserFactory.create_user(email="user1@example.com")
        user2 = UserFactory.create_user(email="user2@example.com")

        client = get_authenticated_client(user1)
        response = client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], user1.id)
        self.assertEqual(response.data["email"], "user1@example.com")
        self.assertNotEqual(response.data["id"], user2.id)

    def test_update_current_user_first_name_returns_200(self):
        """Test PATCH /me/ updates first_name."""
        client = get_authenticated_client(self.user)
        data = {"first_name": "UpdatedFirst"}
        response = client.patch(self.me_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "UpdatedFirst")

    def test_update_current_user_last_name_returns_200(self):
        """Test PATCH /me/ updates last_name."""
        client = get_authenticated_client(self.user)
        data = {"last_name": "UpdatedLast"}
        response = client.patch(self.me_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, "UpdatedLast")

    def test_full_update_with_put_returns_200(self):
        """Test PUT /me/ updates both names."""
        client = get_authenticated_client(self.user)
        data = {"first_name": "NewFirst", "last_name": "NewLast"}
        response = client.put(self.me_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "NewFirst")
        self.assertEqual(self.user.last_name, "NewLast")

    def test_cannot_update_email_via_me_endpoint(self):
        """Test email cannot be updated via /me/ endpoint."""
        client = get_authenticated_client(self.user)
        original_email = self.user.email
        data = {"email": "newemail@example.com", "first_name": "Updated"}
        response = client.patch(self.me_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, original_email)
        self.assertEqual(self.user.first_name, "Updated")

    def test_cannot_update_id_via_me_endpoint(self):
        """Test user ID cannot be changed via /me/ endpoint."""
        client = get_authenticated_client(self.user)
        original_id = self.user.id
        data = {"id": 999, "first_name": "Updated"}
        response = client.patch(self.me_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.id, original_id)


class JWTAuthenticationTest(APITestCase):
    """Integration tests for JWT token authentication."""

    def setUp(self):
        self.user = UserFactory.create_user(
            email="jwtuser@example.com", password="JWTPass123!"
        )
        self.token_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")
        self.me_url = reverse("current_user")

    def test_obtain_token_with_valid_credentials_returns_200(self):
        """Test obtaining JWT token with valid credentials."""
        data = {"email": "jwtuser@example.com", "password": "JWTPass123!"}
        response = self.client.post(self.token_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obtain_token_with_invalid_password_returns_401(self):
        """Test obtaining token with wrong password returns 401."""
        data = {"email": "jwtuser@example.com", "password": "WrongPassword123!"}
        response = self.client.post(self.token_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_token_with_nonexistent_email_returns_401(self):
        """Test obtaining token with non-existent email returns 401."""
        data = {"email": "nonexistent@example.com", "password": "TestPass123!"}
        response = self.client.post(self.token_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_token_grants_access_to_protected_endpoints(self):
        """Test access token allows access to protected endpoints."""
        token_response = self.client.post(
            self.token_url, {"email": "jwtuser@example.com", "password": "JWTPass123!"}
        )
        access_token = token_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "jwtuser@example.com")

    def test_invalid_token_returns_401(self):
        """Test invalid token returns 401 Unauthorized."""
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token_here")
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_returns_new_access_token(self):
        """Test refresh token returns new access token."""
        token_response = self.client.post(
            self.token_url, {"email": "jwtuser@example.com", "password": "JWTPass123!"}
        )
        refresh_token = token_response.data["refresh"]

        refresh_response = self.client.post(
            self.refresh_url, {"refresh": refresh_token}
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_no_authentication_returns_401(self):
        """Test accessing protected endpoint without token returns 401."""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordResetAPITest(APITestCase):
    """Integration tests for password reset request/confirm endpoints."""

    def setUp(self):
        cache.clear()
        self.user = UserFactory.create_user(
            email="resetuser@example.com", password="OldPass123!"
        )
        self.request_url = reverse("password_reset_request")
        self.confirm_url = reverse("password_reset_confirm")

    @patch("users.views.email_service.send_password_reset_email", return_value=True)
    def test_request_password_reset_for_existing_user_creates_token(
        self, mock_send_email
    ):
        """Requesting reset for an existing user should create an active token."""
        response = self.client.post(self.request_url, {"email": self.user.email})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertTrue(PasswordReset.objects.filter(user=self.user, used=False).exists())
        mock_send_email.assert_called_once()

    @patch("users.views.email_service.send_password_reset_email", return_value=True)
    def test_request_password_reset_for_unknown_user_returns_generic_success(
        self, mock_send_email
    ):
        """Unknown emails must still return generic success to prevent enumeration."""
        response = self.client.post(self.request_url, {"email": "unknown@example.com"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        mock_send_email.assert_not_called()

    @patch("users.views.email_service.send_password_reset_email", return_value=True)
    def test_password_reset_request_is_rate_limited_but_still_returns_200(
        self, mock_send_email
    ):
        """Scoped throttling should eventually return 429 for burst reset requests."""
        responses = []
        for _ in range(6):
            responses.append(self.client.post(self.request_url, {"email": self.user.email}))

        self.assertEqual(responses[-1].status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertGreaterEqual(mock_send_email.call_count, 1)

    def test_confirm_password_reset_with_valid_token_updates_password(self):
        """Valid token should change password and mark token as used."""
        reset = PasswordReset.create_for_user(self.user)
        new_password = "BrandNewPass123!"

        response = self.client.post(
            self.confirm_url,
            {
                "token": reset.token,
                "password": new_password,
                "password_confirm": new_password,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        reset.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        self.assertTrue(reset.used)

    def test_confirm_password_reset_with_invalid_token_returns_400(self):
        """Invalid token should be rejected."""
        response = self.client.post(
            self.confirm_url,
            {
                "token": "invalid-token",
                "password": "BrandNewPass123!",
                "password_confirm": "BrandNewPass123!",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("token", response.data)
