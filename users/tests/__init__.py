from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


def get_authenticated_client(user):
    """Helper to create APIClient with JWT token for user."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client
