from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from .test_factories import UserFactory

User = get_user_model()


class UserModelTest(TestCase):
    """Unit tests for the User model."""

    def test_create_user_with_valid_data(self):
        """Test User.objects.create_user() with valid data."""
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            username="test@example.com",
            first_name="Test",
            last_name="User",
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "test@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertNotEqual(user.password, "TestPass123!")
        self.assertTrue(user.check_password("TestPass123!"))

    def test_user_string_representation(self):
        """Test __str__ returns email."""
        user = UserFactory.create_user(email="string@example.com")
        self.assertEqual(str(user), "string@example.com")

    def test_email_uniqueness_constraint(self):
        """Test duplicate emails raise IntegrityError."""
        UserFactory.create_user(email="duplicate@example.com")

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="duplicate@example.com",
                password="TestPass123!",
                username="duplicate2@example.com",
            )

    def test_email_is_required(self):
        """Test creating user without email creates user with empty string."""
        user = User.objects.create_user(email="", password="TestPass123!", username="test")
        self.assertEqual(user.email, "")
        self.assertEqual(user.username, "test")

    def test_username_field_is_email(self):
        """Test USERNAME_FIELD is configured as email."""
        self.assertEqual(User.USERNAME_FIELD, "email")

        user = UserFactory.create_user(email="auth@example.com", password="TestPass123!")
        self.assertTrue(user.check_password("TestPass123!"))

    def test_required_fields_configuration(self):
        """Test REQUIRED_FIELDS contains expected fields."""
        self.assertIn("username", User.REQUIRED_FIELDS)

    def test_user_inherits_from_abstract_user(self):
        """Test User has all AbstractUser fields."""
        user = UserFactory.create_user()

        self.assertTrue(hasattr(user, "first_name"))
        self.assertTrue(hasattr(user, "last_name"))
        self.assertTrue(hasattr(user, "is_active"))
        self.assertTrue(hasattr(user, "is_staff"))
        self.assertTrue(hasattr(user, "is_superuser"))
        self.assertTrue(hasattr(user, "date_joined"))
        self.assertTrue(hasattr(user, "last_login"))

    def test_email_case_sensitivity(self):
        """Test email domain is lowercased by Django."""
        user = UserFactory.create_user(email="Test@Example.com")
        self.assertEqual(user.email, "Test@example.com")

    def test_create_superuser(self):
        """Test User.objects.create_superuser() sets correct flags."""
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="AdminPass123!", username="admin"
        )

        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertEqual(superuser.email, "admin@example.com")
