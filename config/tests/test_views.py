"""Tests for config views."""

import json

from django.test import TestCase

from config.views import api_root


class APIRootViewTest(TestCase):
    """Test suite for API root endpoint."""

    def test_api_root_returns_json_response(self):
        """Test that api_root returns JSON response."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/")
        response = api_root(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_api_root_contains_welcome_message(self):
        """Test that api_root contains welcome message."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/")
        response = api_root(request)
        data = json.loads(response.content)

        self.assertIn("message", data)
        self.assertIn("Travel Itinerary API", data["message"])

    def test_api_root_contains_version(self):
        """Test that api_root contains version information."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/")
        response = api_root(request)
        data = json.loads(response.content)

        self.assertIn("version", data)
        self.assertIsNotNone(data["version"])

    def test_api_root_contains_endpoints(self):
        """Test that api_root contains endpoints information."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/")
        response = api_root(request)
        data = json.loads(response.content)

        self.assertIn("endpoints", data)
        self.assertIsInstance(data["endpoints"], dict)

    def test_api_root_contains_authentication_endpoints(self):
        """Test that api_root contains authentication endpoints."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/")
        response = api_root(request)
        data = json.loads(response.content)

        self.assertIn("authentication", data["endpoints"])
        auth_endpoints = data["endpoints"]["authentication"]

        self.assertIn("register", auth_endpoints)
        self.assertIn("token", auth_endpoints)
        self.assertIn("token_refresh", auth_endpoints)

    def test_api_root_contains_itineraries_endpoints(self):
        """Test that api_root contains itineraries endpoints."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/")
        response = api_root(request)
        data = json.loads(response.content)

        self.assertIn("itineraries", data["endpoints"])

    def test_api_root_contains_admin_endpoint(self):
        """Test that api_root contains admin endpoint."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/")
        response = api_root(request)
        data = json.loads(response.content)

        self.assertIn("admin", data["endpoints"])
        self.assertEqual(data["endpoints"]["admin"], "/admin/")

    def test_api_root_contains_documentation_info(self):
        """Test that api_root contains documentation information."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/")
        response = api_root(request)
        data = json.loads(response.content)

        self.assertIn("documentation", data)

    def test_api_root_endpoint_urls_are_valid(self):
        """Test that endpoint URLs in api_root are valid."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/")
        response = api_root(request)
        data = json.loads(response.content)

        # Check authentication URLs
        auth_endpoints = data["endpoints"]["authentication"]
        self.assertTrue(auth_endpoints["register"].startswith("/api/"))
        self.assertTrue(auth_endpoints["token"].startswith("/api/"))
        self.assertTrue(auth_endpoints["token_refresh"].startswith("/api/"))

        # Check admin URL
        self.assertTrue(data["endpoints"]["admin"].startswith("/admin/"))

    def test_api_root_response_structure(self):
        """Test that api_root response has correct structure."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/")
        response = api_root(request)
        data = json.loads(response.content)

        # Check top-level keys
        required_keys = ["message", "version", "endpoints", "documentation"]
        for key in required_keys:
            self.assertIn(key, data, f"Required key {key} not in response")

        # Check endpoints structure
        self.assertIsInstance(data["endpoints"], dict)
        self.assertIn("admin", data["endpoints"])
        self.assertIn("authentication", data["endpoints"])
        self.assertIn("itineraries", data["endpoints"])

        # Check authentication is a dict
        self.assertIsInstance(data["endpoints"]["authentication"], dict)
        self.assertIsInstance(data["endpoints"]["itineraries"], dict)
