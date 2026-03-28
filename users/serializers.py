from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import PasswordReset

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile (read/update)."""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "profile_image"]
        read_only_fields = ["id", "email"]


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile (first_name, last_name, profile_image)."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "profile_image"]


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password validation."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "password_confirm", "first_name", "last_name"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            username=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class RequestPasswordResetSerializer(serializers.Serializer):
    """Serializer for requesting a password reset."""

    email = serializers.EmailField()

    def validate_email(self, value):
        # Normalize email to lowercase
        return value.lower()


class ConfirmPasswordResetSerializer(serializers.Serializer):
    """Serializer for confirming password reset with token."""

    token = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # Validate passwords match
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )

        # Validate token exists and is valid
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

        # Store the reset object for use in the view
        attrs["reset"] = reset
        return attrs
