"""Tests for itineraries URL configuration."""

from django.test import TestCase
from rest_framework.routers import DefaultRouter

from itineraries.urls import router, urlpatterns
from itineraries.views import ItineraryViewSet, PublicItineraryViewSet


class ItinerariesURLConfigTest(TestCase):
    """Test suite for itineraries URL configuration."""

    def test_router_is_default_router(self):
        """Test that router is an instance of DefaultRouter."""
        self.assertIsInstance(router, DefaultRouter)

    def test_itinerary_viewset_registered(self):
        """Test that ItineraryViewSet is registered with correct basename."""
        registry = {reg[0] for reg in router.registry}
        self.assertIn("my", registry)

        # Find the registration for 'my'
        for prefix, viewset, basename in router.registry:
            if prefix == "my":
                self.assertEqual(viewset, ItineraryViewSet)
                self.assertEqual(basename, "itinerary")

    def test_public_itinerary_viewset_registered(self):
        """Test that PublicItineraryViewSet is registered with correct basename."""
        registry = {reg[0] for reg in router.registry}
        self.assertIn("public", registry)

        # Find the registration for 'public'
        for prefix, viewset, basename in router.registry:
            if prefix == "public":
                self.assertEqual(viewset, PublicItineraryViewSet)
                self.assertEqual(basename, "public-itinerary")

    def test_urlpatterns_configured(self):
        """Test that urlpatterns includes router URLs."""
        self.assertIsNotNone(urlpatterns)
        self.assertGreater(len(urlpatterns), 0)

    def test_router_urls_included(self):
        """Test that router.urls are included in urlpatterns."""
        # The urlpatterns should include the router URLs
        self.assertEqual(len(urlpatterns), 1)

    def test_router_generates_correct_url_patterns(self):
        """Test that router generates the expected URL patterns."""
        # Get all URL patterns from the router
        router_urls = router.urls

        # Check that we have the expected patterns
        pattern_names = [url.name for url in router_urls if hasattr(url, "name")]

        expected_patterns = [
            "itinerary-list",
            "itinerary-detail",
            "public-itinerary-list",
            "public-itinerary-detail",
        ]

        for pattern in expected_patterns:
            self.assertIn(
                pattern, pattern_names, f"Expected pattern {pattern} not found"
            )

    def test_my_prefix_in_router(self):
        """Test that 'my' prefix is registered."""
        prefixes = [reg[0] for reg in router.registry]
        self.assertIn("my", prefixes)

    def test_public_prefix_in_router(self):
        """Test that 'public' prefix is registered."""
        prefixes = [reg[0] for reg in router.registry]
        self.assertIn("public", prefixes)

    def test_router_has_two_viewsets(self):
        """Test that router has exactly two viewsets registered."""
        self.assertEqual(len(router.registry), 2)
