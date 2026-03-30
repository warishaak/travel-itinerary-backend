"""Tests for create_admin management command."""

from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

User = get_user_model()


class CreateAdminCommandTest(TestCase):
    """Test suite for create_admin management command."""

    def test_command_creates_new_admin_user(self):
        """Test that command creates a new admin user when none exists."""
        # Ensure no admin user exists
        self.assertFalse(User.objects.filter(email="test@example.com").exists())

        with patch.dict(
            "os.environ",
            {
                "ADMIN_EMAIL": "test@example.com",
                "ADMIN_USERNAME": "testadmin",
                "ADMIN_PASSWORD": "testpass123",  # nosec B106
            },
        ):
            out = StringIO()
            call_command("create_admin", stdout=out)

            # Check that user was created
            user = User.objects.get(email="test@example.com")
            self.assertEqual(user.username, "testadmin")
            self.assertTrue(user.is_staff)
            self.assertTrue(user.is_superuser)
            self.assertTrue(user.check_password("testpass123"))  # nosec B106

            # Check output message
            self.assertIn("Created admin user", out.getvalue())

    def test_command_updates_existing_user_to_admin(self):
        """Test that command updates existing user to admin."""
        # Create a regular user first
        user = User.objects.create_user(
            email="existing@example.com",
            username="existing",
            password="oldpass",  # nosec B106
            is_staff=False,
            is_superuser=False,
        )

        with patch.dict(
            "os.environ",
            {
                "ADMIN_EMAIL": "existing@example.com",
                "ADMIN_USERNAME": "existingadmin",
                "ADMIN_PASSWORD": "newpass123",
            },
        ):
            out = StringIO()
            call_command("create_admin", stdout=out)

            # Refresh user from database
            user.refresh_from_db()

            # Check that user was updated
            self.assertTrue(user.is_staff)
            self.assertTrue(user.is_superuser)
            self.assertTrue(user.check_password("newpass123"))

            # Check output message
            self.assertIn("Updated admin user", out.getvalue())

    def test_command_fails_when_required_env_vars_missing(self):
        """Test command fails fast when required admin secrets are not set."""
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(CommandError):
                call_command("create_admin", stdout=StringIO())

    def test_command_updates_password_for_existing_admin(self):
        """Test that command updates password for existing admin."""
        # Create an admin user
        user = User.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="oldpassword",  # nosec B106
        )

        with patch.dict(
            "os.environ",
            {
                "ADMIN_EMAIL": "admin@example.com",
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "newpassword123",
            },
        ):
            call_command("create_admin", stdout=StringIO())

            # Refresh and check password was updated
            user.refresh_from_db()
            self.assertTrue(user.check_password("newpassword123"))
            self.assertFalse(user.check_password("oldpassword"))

    def test_command_ensures_superuser_flags(self):
        """Test that command ensures is_staff and is_superuser are True."""
        # Create a user without admin flags
        user = User.objects.create_user(
            email="admin@example.com",
            username="admin",
            password="pass",  # nosec B106
            is_staff=False,
            is_superuser=False,
        )

        with patch.dict(
            "os.environ",
            {
                "ADMIN_EMAIL": "admin@example.com",
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "pass",
            },
        ):
            call_command("create_admin", stdout=StringIO())

        # Refresh and check flags were set
        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_command_output_format(self):
        """Test that command outputs properly formatted messages."""
        out = StringIO()
        with patch.dict(
            "os.environ",
            {
                "ADMIN_EMAIL": "admin@example.com",
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "pass",
            },
        ):
            call_command("create_admin", stdout=out)
        output = out.getvalue()

        # Check output contains expected elements
        self.assertIn("admin", output)
        self.assertIn("admin@example.com", output)
        self.assertIn("✓", output)

    def test_command_with_custom_email(self):
        """Test command with custom email address."""
        with patch.dict(
            "os.environ",
            {
                "ADMIN_EMAIL": "custom@example.com",
                "ADMIN_USERNAME": "customadmin",
                "ADMIN_PASSWORD": "custompass",
            },
        ):
            call_command("create_admin", stdout=StringIO())

            user = User.objects.get(email="custom@example.com")
            self.assertEqual(user.username, "customadmin")
            self.assertTrue(user.check_password("custompass"))

    def test_command_is_idempotent(self):
        """Test that running command multiple times is safe."""
        # Run command twice
        with patch.dict(
            "os.environ",
            {
                "ADMIN_EMAIL": "admin@example.com",
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "pass",
            },
        ):
            call_command("create_admin", stdout=StringIO())
            call_command("create_admin", stdout=StringIO())

        # Should only have one admin user
        admin_users = User.objects.filter(email="admin@example.com")
        self.assertEqual(admin_users.count(), 1)

        # User should still be a superuser
        user = admin_users.first()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
