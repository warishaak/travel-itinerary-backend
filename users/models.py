import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom user model using email as the unique identifier."""

    email = models.EmailField(unique=True)
    profile_image = models.URLField(max_length=500, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class PasswordReset(models.Model):
    """Model for storing password reset tokens."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_resets"
    )
    token = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Password reset for {self.user.email} at {self.created_at}"

    def is_valid(self):
        """Check if token is valid (not used and not expired)."""
        if self.used:
            return False
        expiry = self.created_at + timezone.timedelta(hours=1)
        return timezone.now() < expiry

    @classmethod
    def create_for_user(cls, user):
        """Create new reset token for user, invalidating old ones."""
        # Delete old unused tokens for this user
        cls.objects.filter(user=user, used=False).delete()

        # Generate cryptographically secure token
        token = secrets.token_urlsafe(32)

        # Create and return new token
        return cls.objects.create(user=user, token=token)
