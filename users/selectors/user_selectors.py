from django.contrib.auth import get_user_model

from users.models import PasswordReset

User = get_user_model()


def get_user_by_email(email):
    return User.objects.get(email=email)


def get_password_reset_by_token(token):
    return PasswordReset.objects.get(token=token)
