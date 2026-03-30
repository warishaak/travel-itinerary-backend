import logging

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from config.email_service import email_service

from .models import PasswordReset
from .serializers import (
    ConfirmPasswordResetSerializer,
    RegisterSerializer,
    RequestPasswordResetSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
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
    """Protected endpoint to get and update the currently authenticated user."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


class RequestPasswordResetView(APIView):
    """
    Endpoint to request a password reset.
    Accepts email, sends reset link if user exists.
    Always returns 200 to prevent user enumeration.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        # Rate limiting: 3 requests per email per 15 minutes
        cache_key = f"password_reset_rate_limit:{email}"
        attempts = cache.get(cache_key, 0)

        if attempts >= 3:
            logger.warning(f"Rate limit exceeded for password reset: {email}")
            # Still return success to prevent enumeration
            return Response(
                {
                    "message": "If an account exists with that email, you'll receive a password reset link."
                },
                status=status.HTTP_200_OK,
            )

        # Increment rate limit counter
        cache.set(cache_key, attempts + 1, 900)  # 15 minutes

        # Try to find user
        try:
            user = User.objects.get(email=email)

            # Create reset token
            reset = PasswordReset.create_for_user(user)

            # Send email
            success = email_service.send_password_reset_email(
                user_email=user.email,
                user_name=user.first_name or user.email.split("@")[0],
                reset_token=reset.token,
            )

            if success:
                logger.info(f"Password reset email sent to {email}")
            else:
                logger.error(f"Failed to send password reset email to {email}")

        except User.DoesNotExist:
            # User doesn't exist - log it but don't expose this to the client
            logger.info(f"Password reset requested for non-existent email: {email}")

        # Always return the same response (prevent user enumeration)
        return Response(
            {
                "message": "If an account exists with that email, you'll receive a password reset link."
            },
            status=status.HTTP_200_OK,
        )


class ConfirmPasswordResetView(APIView):
    """
    Endpoint to confirm password reset with token.
    Validates token and sets new password.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset_confirm"

    def post(self, request):
        serializer = ConfirmPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset = serializer.validated_data["reset"]
        new_password = serializer.validated_data["password"]

        # Set new password
        user = reset.user
        user.set_password(new_password)
        user.save()

        # Mark token as used
        reset.used = True
        reset.save()

        logger.info(f"Password reset successful for user: {user.email}")

        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """Public JWT login endpoint with scoped throttling."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"


class ThrottledTokenRefreshView(TokenRefreshView):
    """Public JWT refresh endpoint with scoped throttling."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_token_refresh"
