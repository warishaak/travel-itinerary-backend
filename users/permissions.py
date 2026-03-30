from rest_framework.permissions import BasePermission


class PublicAuthPermission(BasePermission):
    """Allow anonymous access to explicit public authentication endpoints."""

    def has_permission(self, request, view):
        return True


class IsAuthenticatedUserPermission(BasePermission):
    """Allow only authenticated users."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
