import logging

from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.api.serializers import (
    ConfirmPasswordResetInputSerializer,
    RegisterInputSerializer,
    RequestPasswordResetInputSerializer,
    UserReadSerializer,
    UserUpdateInputSerializer,
)
from users.domain.rules import PASSWORD_RESET_GENERIC_MESSAGE
from users.permissions import IsAuthenticatedUserPermission, PublicAuthPermission
from users.services.password_reset_service import PasswordResetService

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""

    serializer_class = RegisterInputSerializer
    permission_classes = [PublicAuthPermission]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_register"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "message": "User created successfully",
            },
            status=status.HTTP_201_CREATED,
        )


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Protected endpoint to retrieve and update the authenticated user."""

    permission_classes = [IsAuthenticatedUserPermission]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateInputSerializer
        return UserReadSerializer

    def get_object(self):
        return self.request.user


class RequestPasswordResetView(APIView):
    """Request password reset while preventing user enumeration."""

    permission_classes = [PublicAuthPermission]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    def post(self, request):
        serializer = RequestPasswordResetInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        cache_key = f"password_reset_rate_limit:{email}"
        attempts = cache.get(cache_key, 0)

        if attempts >= 3:
            logger.warning(f"Rate limit exceeded for password reset: {email}")
            return Response({"message": PASSWORD_RESET_GENERIC_MESSAGE}, status=200)

        cache.set(cache_key, attempts + 1, 900)
        PasswordResetService.request_password_reset(email)

        return Response(
            {"message": PASSWORD_RESET_GENERIC_MESSAGE},
            status=status.HTTP_200_OK,
        )


class ConfirmPasswordResetView(APIView):
    """Confirm password reset by token and update password."""

    permission_classes = [PublicAuthPermission]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset_confirm"

    def post(self, request):
        serializer = ConfirmPasswordResetInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset = serializer.validated_data["reset"]
        new_password = serializer.validated_data["password"]
        PasswordResetService.confirm_password_reset(reset, new_password)

        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """Public JWT login endpoint with scoped throttling."""

    permission_classes = [PublicAuthPermission]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"


class ThrottledTokenRefreshView(TokenRefreshView):
    """Public JWT refresh endpoint with scoped throttling."""

    permission_classes = [PublicAuthPermission]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_token_refresh"
