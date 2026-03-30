from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.domain.rules import normalize_email
from users.models import PasswordReset
from users.services.user_service import UserService

User = get_user_model()


class UserReadSerializer(serializers.ModelSerializer):
    """Output DTO for user profile responses."""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "profile_image"]
        read_only_fields = ["id", "email"]


class UserUpdateInputSerializer(serializers.ModelSerializer):
    """Input DTO for updating profile data."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "profile_image"]


class RegisterInputSerializer(serializers.ModelSerializer):
    """Input DTO for user registration."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "password_confirm", "first_name", "last_name"]

    def validate_email(self, value):
        normalized = normalize_email(value)
        if User.objects.filter(email=normalized).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        return UserService.register_user(validated_data)


class RequestPasswordResetInputSerializer(serializers.Serializer):
    """Input DTO for password reset requests."""

    email = serializers.EmailField()

    def validate_email(self, value):
        return normalize_email(value)


class ConfirmPasswordResetInputSerializer(serializers.Serializer):
    """Input DTO for password reset confirmation."""

    token = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )

        try:
            reset = PasswordReset.objects.get(token=attrs["token"])
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError(
                {"token": "Token is invalid or has expired."}
            )

        if not reset.is_valid():
            raise serializers.ValidationError(
                {"token": "Token is invalid or has expired."}
            )

        attrs["reset"] = reset
        return attrs
