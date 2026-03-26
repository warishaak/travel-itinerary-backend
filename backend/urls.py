from django.urls import include, path

# Admin is temporarily disabled to fix migration dependency issues
# from django.contrib import admin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/itineraries/", include("itineraries.urls")),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
