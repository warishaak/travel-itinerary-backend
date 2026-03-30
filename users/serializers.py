from users.api.serializers import (
    ConfirmPasswordResetInputSerializer,
    RegisterInputSerializer,
    RequestPasswordResetInputSerializer,
    UserReadSerializer,
    UserUpdateInputSerializer,
)

# Backward-compatible aliases for existing imports/tests.
UserSerializer = UserReadSerializer
UserUpdateSerializer = UserUpdateInputSerializer
RegisterSerializer = RegisterInputSerializer
RequestPasswordResetSerializer = RequestPasswordResetInputSerializer
ConfirmPasswordResetSerializer = ConfirmPasswordResetInputSerializer

__all__ = [
    "UserReadSerializer",
    "UserUpdateInputSerializer",
    "RegisterInputSerializer",
    "RequestPasswordResetInputSerializer",
    "ConfirmPasswordResetInputSerializer",
    "UserSerializer",
    "UserUpdateSerializer",
    "RegisterSerializer",
    "RequestPasswordResetSerializer",
    "ConfirmPasswordResetSerializer",
]
