from django.core.management.base import BaseCommand

from config.email_service import email_service


class Command(BaseCommand):
    help = "Send a test email using SendGrid"

    def add_arguments(self, parser):
        parser.add_argument(
            "email",
            type=str,
            help="Email address to send test email to",
        )
        parser.add_argument(
            "--type",
            type=str,
            choices=["simple", "welcome", "itinerary"],
            default="simple",
            help="Type of email to send (default: simple)",
        )
        parser.add_argument(
            "--name",
            type=str,
            default="Test User",
            help="User name for welcome/itinerary emails (default: Test User)",
        )
        parser.add_argument(
            "--itinerary-title",
            type=str,
            default="Trip to Paris",
            help="Itinerary title for itinerary emails (default: Trip to Paris)",
        )

    def handle(self, *args, **options):
        email = options["email"]
        email_type = options["type"]
        name = options["name"]
        itinerary_title = options["itinerary_title"]

        self.stdout.write(f"Sending {email_type} email to {email}...")

        success = False

        try:
            if email_type == "simple":
                success = email_service.send_email(
                    to_emails=email,
                    subject="Test Email from Travel Itinerary Backend",
                    html_content="<p>This is a test email from your Travel Itinerary Backend.</p>",
                    plain_text_content="This is a test email from your Travel Itinerary Backend.",
                )

            elif email_type == "welcome":
                success = email_service.send_welcome_email(
                    user_email=email, user_name=name
                )

            elif email_type == "itinerary":
                success = email_service.send_itinerary_confirmation_email(
                    user_email=email, user_name=name, itinerary_title=itinerary_title
                )

            if success:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Email sent successfully to {email}")
                )
                self.stdout.write("Status: 202 (Email queued for delivery by SendGrid)")
            else:
                self.stdout.write(
                    self.style.ERROR(f"✗ Failed to send email to {email}")
                )
                self.stdout.write(
                    "Check your SendGrid API key and configuration in .env file"
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error: {e}"))
