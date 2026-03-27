from django.http import JsonResponse


def api_root(request):
    """Root endpoint with API information."""
    return JsonResponse(
        {
            "message": "Welcome to Travel Itinerary API",
            "version": "1.0",
            "endpoints": {
                "admin": "/admin/",
                "authentication": {
                    "register": "/api/auth/register/",
                    "login": "/api/auth/login/",
                    "token": "/api/auth/token/",
                    "token_refresh": "/api/auth/token/refresh/",
                },
                "itineraries": {
                    "list_create": "/api/itineraries/",
                    "detail": "/api/itineraries/{id}/",
                },
            },
            "documentation": "Visit /admin/ for the admin panel",
        }
    )
