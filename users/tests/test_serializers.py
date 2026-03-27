from django.contrib.auth import get_user_model
from django.test import TestCase

from users.serializers import RegisterSerializer, UserSerializer, UserUpdateSerializer

from .test_factories import UserFactory

User = get_user_model()


class RegisterSerializerTest(TestCase):
    """Unit tests for RegisterSerializer."""

    def test_valid_registration_data_serialization(self):
        """Test serializer with valid registration data."""
        data = UserFactory.build_registration_data()
        serializer = RegisterSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertIn("email", serializer.validated_data)
        self.assertIn("password", serializer.validated_data)
        self.assertIn("password_confirm", serializer.validated_data)

    def test_password_and_password_confirm_match(self):
        """Test validation passes when passwords match."""
        data = UserFactory.build_registration_data(password="TestPass123!")
        serializer = RegisterSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_password_and_password_confirm_mismatch_raises_error(self):
        """Test validation fails when passwords don't match."""
        data = UserFactory.build_password_mismatch_data()
        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)
        self.assertEqual(
            str(serializer.errors["password_confirm"][0]), "Passwords do not match."
        )

    def test_duplicate_email_raises_validation_error(self):
        """Test validation fails for duplicate email."""
        existing_user = UserFactory.create_user(email="existing@example.com")
        data = UserFactory.build_duplicate_email_data(existing_user)
        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertIn("already exists", str(serializer.errors["email"][0]))

    def test_weak_password_fails_django_validators(self):
        """Test weak passwords fail Django password validators."""
        weak_passwords = UserFactory.build_weak_password_data()

        for data in weak_passwords:
            data.update({"first_name": "Test", "last_name": "User"})
            serializer = RegisterSerializer(data=data)
            self.assertFalse(
                serializer.is_valid(), f"Password {data['password']} should fail"
            )
            self.assertIn("password", serializer.errors)

    def test_password_similar_to_email_fails_validation(self):
        """Test password similar to email fails validation."""
        data = UserFactory.build_registration_data(
            email="john@example.com", password="john123", password_confirm="john123"
        )
        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_numeric_only_password_fails_validation(self):
        """Test numeric-only password fails validation."""
        data = UserFactory.build_registration_data(
            password="12345678", password_confirm="12345678"
        )
        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_common_password_fails_validation(self):
        """Test common passwords fail validation."""
        common_passwords = ["password", "12345678"]

        for pwd in common_passwords:
            data = UserFactory.build_registration_data(
                password=pwd, password_confirm=pwd
            )
            serializer = RegisterSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn("password", serializer.errors)

    def test_password_min_length_validation(self):
        """Test password minimum length validation."""
        data = UserFactory.build_registration_data(
            password="Test1!", password_confirm="Test1!"
        )
        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_create_method_creates_user_correctly(self):
        """Test serializer.save() creates user in database."""
        data = UserFactory.build_registration_data(
            email="create@example.com",
            password="CreatePass123!",
            password_confirm="CreatePass123!",
            first_name="Create",
            last_name="Test",
        )
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertEqual(user.email, "create@example.com")
        self.assertEqual(user.username, "create@example.com")
        self.assertEqual(user.first_name, "Create")
        self.assertEqual(user.last_name, "Test")
        self.assertTrue(user.check_password("CreatePass123!"))
        self.assertNotEqual(user.password, "CreatePass123!")

    def test_create_method_removes_password_confirm_field(self):
        """Test password_confirm is not passed to User.objects.create_user()."""
        data = UserFactory.build_registration_data()
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertFalse(hasattr(user, "password_confirm"))

    def test_password_is_write_only(self):
        """Test password field is not in serialized output."""
        user = UserFactory.create_user()
        serializer = RegisterSerializer(user)

        self.assertNotIn("password", serializer.data)
        self.assertNotIn("password_confirm", serializer.data)

    def test_optional_name_fields(self):
        """Test registration succeeds without first_name and last_name."""
        data = {
            "email": "noname@example.com",
            "password": "TestPass123!",
            "password_confirm": "TestPass123!",
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertEqual(user.first_name, "")
        self.assertEqual(user.last_name, "")


class UserSerializerTest(TestCase):
    """Unit tests for UserSerializer."""

    def test_user_serialization_includes_correct_fields(self):
        """Test serializer includes correct fields."""
        user = UserFactory.create_user(
            email="fields@example.com", first_name="Field", last_name="Test"
        )
        serializer = UserSerializer(user)

        self.assertIn("id", serializer.data)
        self.assertIn("email", serializer.data)
        self.assertIn("first_name", serializer.data)
        self.assertIn("last_name", serializer.data)
        self.assertEqual(serializer.data["email"], "fields@example.com")
        self.assertEqual(serializer.data["first_name"], "Field")
        self.assertEqual(serializer.data["last_name"], "Test")

    def test_email_is_read_only(self):
        """Test email cannot be updated via serializer."""
        user = UserFactory.create_user(email="readonly@example.com")
        data = {"email": "newemail@example.com", "first_name": "Updated"}
        serializer = UserSerializer(user, data=data, partial=True)

        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.email, "readonly@example.com")
        self.assertEqual(updated_user.first_name, "Updated")

    def test_id_is_read_only(self):
        """Test id cannot be set via serializer."""
        user = UserFactory.create_user()
        original_id = user.id
        data = {"id": 999, "first_name": "Test"}
        serializer = UserSerializer(user, data=data, partial=True)

        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.id, original_id)


class UserUpdateSerializerTest(TestCase):
    """Unit tests for UserUpdateSerializer."""

    def test_update_serializer_only_allows_name_fields(self):
        """Test serializer only includes first_name and last_name."""
        user = UserFactory.create_user()
        serializer = UserUpdateSerializer(user)

        self.assertIn("first_name", serializer.data)
        self.assertIn("last_name", serializer.data)
        self.assertNotIn("id", serializer.data)
        self.assertNotIn("email", serializer.data)

    def test_cannot_update_email_via_update_serializer(self):
        """Test email is ignored in update serializer."""
        user = UserFactory.create_user(email="original@example.com")
        data = {
            "email": "newemail@example.com",
            "first_name": "Updated",
            "last_name": "Name",
        }
        serializer = UserUpdateSerializer(user, data=data)

        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.email, "original@example.com")
        self.assertEqual(updated_user.first_name, "Updated")
        self.assertEqual(updated_user.last_name, "Name")
