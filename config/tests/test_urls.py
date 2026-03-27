"""Tests for URL routing configuration."""
from django.test import TestCase
from django.urls import resolve, reverse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from itineraries.views import ItineraryViewSet, PublicItineraryViewSet
from users.views import CurrentUserView, RegisterView


class URLRoutingTest(TestCase):
    """Test suite for URL routing configuration."""

    def test_admin_url_resolves(self):
        """Test that admin URL resolves correctly."""
        url = reverse("admin:index")
        self.assertEqual(url, "/admin/")

    def test_itinerary_list_url_resolves(self):
        """Test that itinerary list URL resolves correctly."""
        url = reverse("itinerary-list")
        self.assertEqual(url, "/api/itineraries/my/")

        resolver = resolve("/api/itineraries/my/")
        self.assertEqual(resolver.func.cls, ItineraryViewSet)

    def test_itinerary_detail_url_resolves(self):
        """Test that itinerary detail URL resolves correctly."""
        url = reverse("itinerary-detail", kwargs={"pk": 1})
        self.assertEqual(url, "/api/itineraries/my/1/")

        resolver = resolve("/api/itineraries/my/1/")
        self.assertEqual(resolver.func.cls, ItineraryViewSet)

    def test_public_itinerary_list_url_resolves(self):
        """Test that public itinerary list URL resolves correctly."""
        url = reverse("public-itinerary-list")
        self.assertEqual(url, "/api/itineraries/public/")

        resolver = resolve("/api/itineraries/public/")
        self.assertEqual(resolver.func.cls, PublicItineraryViewSet)

    def test_public_itinerary_detail_url_resolves(self):
        """Test that public itinerary detail URL resolves correctly."""
        url = reverse("public-itinerary-detail", kwargs={"pk": 1})
        self.assertEqual(url, "/api/itineraries/public/1/")

        resolver = resolve("/api/itineraries/public/1/")
        self.assertEqual(resolver.func.cls, PublicItineraryViewSet)

    def test_register_url_resolves(self):
        """Test that user registration URL resolves correctly."""
        url = reverse("register")
        self.assertEqual(url, "/api/auth/register/")

        resolver = resolve("/api/auth/register/")
        self.assertEqual(resolver.func.cls, RegisterView)

    def test_current_user_url_resolves(self):
        """Test that current user URL resolves correctly."""
        url = reverse("current_user")
        self.assertEqual(url, "/api/auth/me/")

        resolver = resolve("/api/auth/me/")
        self.assertEqual(resolver.func.cls, CurrentUserView)

    def test_token_obtain_url_resolves(self):
        """Test that token obtain URL resolves correctly."""
        url = reverse("token_obtain_pair")
        self.assertEqual(url, "/api/auth/token/")

        resolver = resolve("/api/auth/token/")
        self.assertEqual(resolver.func.cls, TokenObtainPairView)

    def test_token_refresh_url_resolves(self):
        """Test that token refresh URL resolves correctly."""
        url = reverse("token_refresh")
        self.assertEqual(url, "/api/auth/token/refresh/")

        resolver = resolve("/api/auth/token/refresh/")
        self.assertEqual(resolver.func.cls, TokenRefreshView)

    def test_api_urls_use_correct_prefix(self):
        """Test that all API URLs use /api/ prefix."""
        api_urls = [
            reverse("itinerary-list"),
            reverse("public-itinerary-list"),
            reverse("register"),
            reverse("current_user"),
            reverse("token_obtain_pair"),
            reverse("token_refresh"),
        ]

        for url in api_urls:
            self.assertTrue(
                url.startswith("/api/"), f"URL {url} does not start with /api/ prefix"
            )

    def test_url_patterns_use_trailing_slash(self):
        """Test that URL patterns follow Django convention with trailing slash."""
        urls = [
            reverse("itinerary-list"),
            reverse("public-itinerary-list"),
            reverse("register"),
            reverse("current_user"),
            reverse("token_obtain_pair"),
            reverse("token_refresh"),
        ]

        for url in urls:
            self.assertTrue(
                url.endswith("/"), f"URL {url} does not have trailing slash"
            )

    def test_detail_urls_accept_integer_pk(self):
        """Test that detail URLs accept integer primary keys."""
        urls = [
            ("itinerary-detail", "/api/itineraries/my/123/"),
            ("public-itinerary-detail", "/api/itineraries/public/456/"),
        ]

        for name, expected_url in urls:
            url = reverse(name, kwargs={"pk": 123 if "my" in expected_url else 456})
            self.assertIn(str(123 if "my" in expected_url else 456), url)

    def test_invalid_url_returns_404(self):
        """Test that accessing non-existent URL returns 404."""
        response = self.client.get("/api/nonexistent/")
        self.assertEqual(response.status_code, 404)

    def test_api_root_url_structure(self):
        """Test that API follows RESTful URL structure."""
        # Test nested resources
        self.assertIn("itineraries", reverse("itinerary-list"))
        self.assertIn("auth", reverse("register"))

        # Test resource naming (plural for collections)
        itinerary_list = reverse("itinerary-list")
        self.assertIn("itineraries", itinerary_list)
