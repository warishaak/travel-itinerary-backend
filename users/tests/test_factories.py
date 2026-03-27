import random
import string

from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory:
    """Factory class for creating test User instances and data."""

    @staticmethod
    def build_valid_user_data(**kwargs):
        """Build valid user data dictionary."""
        random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        default_data = {
            "email": f"testuser{random_suffix}@example.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
        }
        default_data.update(kwargs)
        return default_data

    @staticmethod
    def create_user(**kwargs):
        """Create and return a User instance."""
        data = UserFactory.build_valid_user_data(**kwargs)
        email = data.pop("email")
        password = data.pop("password")

        user = User.objects.create_user(
            email=email, password=password, username=email, **data
        )
        return user

    @staticmethod
    def create_multiple_users(count=3, **kwargs):
        """Create multiple User instances."""
        users = []
        for i in range(count):
            data = kwargs.copy()
            data.setdefault("email", f"user{i + 1}@example.com")
            data.setdefault("first_name", f"User{i + 1}")
            data.setdefault("last_name", f"Test{i + 1}")
            user = UserFactory.create_user(**data)
            users.append(user)
        return users

    @staticmethod
    def build_registration_data(**kwargs):
        """Build valid registration data with password_confirm field."""
        data = UserFactory.build_valid_user_data(**kwargs)
        password = data.get("password", "TestPass123!")
        data["password_confirm"] = password
        return data

    @staticmethod
    def build_invalid_email_data():
        """Build registration data with invalid email format."""
        data = UserFactory.build_registration_data()
        data["email"] = "notanemail"
        return data

    @staticmethod
    def build_password_mismatch_data():
        """Build registration data with password mismatch."""
        data = UserFactory.build_registration_data()
        data["password_confirm"] = "DifferentPassword123!"
        return data

    @staticmethod
    def build_weak_password_data():
        """Build registration data with weak passwords."""
        return [
            {"email": "weak1@example.com", "password": "123", "password_confirm": "123"},
            {
                "email": "weak2@example.com",
                "password": "password",
                "password_confirm": "password",
            },
            {
                "email": "weak3@example.com",
                "password": "12345678",
                "password_confirm": "12345678",
            },
        ]

    @staticmethod
    def build_duplicate_email_data(existing_user):
        """Build registration data with an existing email."""
        data = UserFactory.build_registration_data()
        data["email"] = existing_user.email
        return data
