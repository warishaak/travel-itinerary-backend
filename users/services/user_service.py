from django.contrib.auth import get_user_model

User = get_user_model()


class UserService:
    """User use-case service for registration and profile operations."""

    @staticmethod
    def register_user(validated_data):
        payload = validated_data.copy()
        payload.pop("password_confirm")
        return User.objects.create_user(
            email=payload["email"],
            password=payload["password"],
            username=payload["email"],
            first_name=payload.get("first_name", ""),
            last_name=payload.get("last_name", ""),
        )
