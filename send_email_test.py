import os
import sys
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django  # noqa: E402

django.setup()

from config.email_service import email_service  # noqa: E402


def test_simple_email():
    """Test sending a simple email."""
    print("Testing simple email send...")

    to_email = os.getenv("TO_EMAIL", "test@example.com")

    success = email_service.send_email(
        to_emails=to_email,
        subject="Hello from SendGrid - Travel Itinerary Backend",
        html_content="<p>This is a test email from your Travel Itinerary Backend.</p>",
        plain_text_content="This is a test email from your Travel Itinerary Backend.",
    )

    if success:
        print(f"✓ Email sent successfully to {to_email}")
        print("Status: 202 (Email queued for delivery)")
    else:
        print("✗ Failed to send email")

    return success


def test_welcome_email():
    """Test sending a welcome email."""
    print("\nTesting welcome email...")

    to_email = os.getenv("TO_EMAIL", "test@example.com")

    success = email_service.send_welcome_email(
        user_email=to_email, user_name="Test User"
    )

    if success:
        print(f"✓ Welcome email sent successfully to {to_email}")
    else:
        print("✗ Failed to send welcome email")

    return success


def test_itinerary_confirmation_email():
    """Test sending an itinerary confirmation email."""
    print("\nTesting itinerary confirmation email...")

    to_email = os.getenv("TO_EMAIL", "test@example.com")

    success = email_service.send_itinerary_confirmation_email(
        user_email=to_email, user_name="Test User", itinerary_title="Trip to Paris"
    )

    if success:
        print(f"✓ Itinerary confirmation email sent successfully to {to_email}")
    else:
        print("✗ Failed to send itinerary confirmation email")

    return success


if __name__ == "__main__":
    print("=" * 60)
    print("SendGrid Email Test Suite")
    print("=" * 60)

    # Check if SendGrid API key is configured
    if not os.getenv("SENDGRID_API_KEY"):
        print("\n⚠ WARNING: SENDGRID_API_KEY is not set in .env file")
        print("Please add your SendGrid API key to the .env file")
        sys.exit(1)

    print(f"\nSending to: {os.getenv('TO_EMAIL', 'test@example.com')}")
    print(f"From: {os.getenv('FROM_EMAIL', 'noreply@example.com')}")
    print()

    # Run tests
    results = [
        test_simple_email(),
        test_welcome_email(),
        test_itinerary_confirmation_email(),
    ]

    # Print summary
    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)

    if all(results):
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
        sys.exit(1)
