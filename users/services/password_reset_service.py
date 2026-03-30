import logging

from django.contrib.auth import get_user_model

from config.email_service import email_service
from users.models import PasswordReset
from users.selectors.user_selectors import get_user_by_email

User = get_user_model()
logger = logging.getLogger(__name__)


class PasswordResetService:
    """Use-case service for password reset flows."""

    @staticmethod
    def request_password_reset(email):
        try:
            user = get_user_by_email(email)

            reset = PasswordReset.create_for_user(user)
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
            logger.info(f"Password reset requested for non-existent email: {email}")

    @staticmethod
    def confirm_password_reset(reset, new_password):
        user = reset.user
        user.set_password(new_password)
        user.save()

        reset.used = True
        reset.save()

        logger.info(f"Password reset successful for user: {user.email}")
