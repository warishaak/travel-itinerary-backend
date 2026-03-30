PASSWORD_RESET_GENERIC_MESSAGE = "If an account exists with that email, you'll receive a password reset link."  # nosec B105


def normalize_email(value):
    return value.lower()
