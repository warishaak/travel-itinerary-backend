"""Tests for Django settings configuration."""
from django.conf import settings
from django.test import TestCase, override_settings


class SettingsConfigurationTest(TestCase):
    """Test suite for settings configuration."""

    def test_debug_setting_exists(self):
        """Test that DEBUG setting is configured."""
        self.assertIsNotNone(settings.DEBUG)
        self.assertIsInstance(settings.DEBUG, bool)

    def test_secret_key_is_set(self):
        """Test that SECRET_KEY is configured."""
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertGreater(len(settings.SECRET_KEY), 0)

    def test_allowed_hosts_configured(self):
        """Test that ALLOWED_HOSTS is configured."""
        self.assertIsNotNone(settings.ALLOWED_HOSTS)
        self.assertIsInstance(settings.ALLOWED_HOSTS, list)

    def test_custom_user_model_configured(self):
        """Test that custom User model is configured."""
        self.assertEqual(settings.AUTH_USER_MODEL, "users.User")

    def test_installed_apps_includes_required_apps(self):
        """Test that all required apps are installed."""
        required_apps = [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "rest_framework",
            "corsheaders",
            "users",
            "itineraries",
        ]

        for app in required_apps:
            self.assertIn(
                app,
                settings.INSTALLED_APPS,
                f"Required app {app} not in INSTALLED_APPS",
            )

    def test_middleware_order_is_correct(self):
        """Test that middleware is in correct order."""
        middleware_list = settings.MIDDLEWARE

        # SecurityMiddleware should be first
        self.assertEqual(
            middleware_list[0], "django.middleware.security.SecurityMiddleware"
        )

        # CORS should be early (after security)
        cors_index = middleware_list.index("corsheaders.middleware.CorsMiddleware")
        security_index = middleware_list.index(
            "django.middleware.security.SecurityMiddleware"
        )
        self.assertLess(security_index, cors_index)

        # SessionMiddleware before AuthenticationMiddleware
        session_index = middleware_list.index(
            "django.contrib.sessions.middleware.SessionMiddleware"
        )
        auth_index = middleware_list.index(
            "django.contrib.auth.middleware.AuthenticationMiddleware"
        )
        self.assertLess(session_index, auth_index)

    def test_rest_framework_authentication_configured(self):
        """Test that REST framework JWT authentication is configured."""
        rest_config = settings.REST_FRAMEWORK
        self.assertIn("DEFAULT_AUTHENTICATION_CLASSES", rest_config)

        auth_classes = rest_config["DEFAULT_AUTHENTICATION_CLASSES"]
        self.assertIn(
            "rest_framework_simplejwt.authentication.JWTAuthentication", auth_classes
        )

    def test_database_configuration_exists(self):
        """Test that database is configured."""
        self.assertIn("default", settings.DATABASES)
        db_config = settings.DATABASES["default"]
        self.assertIn("ENGINE", db_config)
        self.assertIn("NAME", db_config)

    def test_static_files_configured(self):
        """Test that static files settings are configured."""
        self.assertIsNotNone(settings.STATIC_URL)
        self.assertIsNotNone(settings.STATIC_ROOT)

    def test_cors_configuration_exists(self):
        """Test that CORS settings are configured."""
        self.assertTrue(hasattr(settings, "CORS_ALLOW_CREDENTIALS"))
        self.assertTrue(hasattr(settings, "CORS_ALLOWED_ORIGINS"))

    def test_cors_allows_credentials(self):
        """Test that CORS allows credentials."""
        self.assertTrue(settings.CORS_ALLOW_CREDENTIALS)

    def test_cors_allowed_methods_configured(self):
        """Test that CORS allowed methods are configured."""
        self.assertTrue(hasattr(settings, "CORS_ALLOW_METHODS"))
        required_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

        for method in required_methods:
            self.assertIn(
                method,
                settings.CORS_ALLOW_METHODS,
                f"HTTP method {method} not in CORS_ALLOW_METHODS",
            )

    def test_cors_allowed_headers_configured(self):
        """Test that CORS allowed headers are configured."""
        self.assertTrue(hasattr(settings, "CORS_ALLOW_HEADERS"))
        required_headers = ["authorization", "content-type"]

        for header in required_headers:
            self.assertIn(
                header,
                settings.CORS_ALLOW_HEADERS,
                f"Header {header} not in CORS_ALLOW_HEADERS",
            )

    def test_root_urlconf_configured(self):
        """Test that ROOT_URLCONF is configured."""
        self.assertEqual(settings.ROOT_URLCONF, "config.urls")

    def test_wsgi_application_configured(self):
        """Test that WSGI application is configured."""
        self.assertEqual(settings.WSGI_APPLICATION, "config.wsgi.application")

    def test_default_auto_field_configured(self):
        """Test that DEFAULT_AUTO_FIELD is configured."""
        self.assertEqual(settings.DEFAULT_AUTO_FIELD, "django.db.models.BigAutoField")

    def test_timezone_settings(self):
        """Test that timezone settings are configured."""
        self.assertIsNotNone(settings.TIME_ZONE)
        self.assertIsInstance(settings.USE_TZ, bool)
        self.assertTrue(settings.USE_TZ)

    def test_language_settings(self):
        """Test that language settings are configured."""
        self.assertIsNotNone(settings.LANGUAGE_CODE)
        self.assertIsInstance(settings.USE_I18N, bool)

    @override_settings(DEBUG=False)
    def test_csrf_trusted_origins_in_production(self):
        """Test that CSRF_TRUSTED_ORIGINS is configured for production."""
        # In production mode, CSRF_TRUSTED_ORIGINS should be set
        self.assertTrue(hasattr(settings, "CSRF_TRUSTED_ORIGINS"))

    def test_templates_configured(self):
        """Test that templates are configured."""
        self.assertIsNotNone(settings.TEMPLATES)
        self.assertGreater(len(settings.TEMPLATES), 0)

        template_config = settings.TEMPLATES[0]
        self.assertEqual(
            template_config["BACKEND"],
            "django.template.backends.django.DjangoTemplates",
        )
        self.assertTrue(template_config["APP_DIRS"])

    def test_password_validators_configured(self):
        """Test that password validators are configured."""
        self.assertIsNotNone(settings.AUTH_PASSWORD_VALIDATORS)
        self.assertGreater(len(settings.AUTH_PASSWORD_VALIDATORS), 0)

        # Check for required validators
        validator_names = [v["NAME"] for v in settings.AUTH_PASSWORD_VALIDATORS]
        required_validators = [
            "UserAttributeSimilarityValidator",
            "MinimumLengthValidator",
            "CommonPasswordValidator",
            "NumericPasswordValidator",
        ]

        for validator in required_validators:
            self.assertTrue(
                any(validator in name for name in validator_names),
                f"Required validator {validator} not configured",
            )

    def test_whitenoise_middleware_configured(self):
        """Test that WhiteNoise middleware is configured for static files."""
        self.assertIn("whitenoise.middleware.WhiteNoiseMiddleware", settings.MIDDLEWARE)
