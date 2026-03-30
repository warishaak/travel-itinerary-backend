from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsItineraryOwnerPermission(BasePermission):
    """Only authenticated owners can access their itineraries."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and request.user.is_authenticated and obj.user == request.user
        )


class PublicReadOnlyPermission(BasePermission):
    """Allow unauthenticated read-only access for public resources."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
