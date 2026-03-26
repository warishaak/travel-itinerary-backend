import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create a superuser if one does not exist"

    def handle(self, *args, **options):
        email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        username = os.getenv("ADMIN_USERNAME", "admin")
        password = os.getenv("ADMIN_PASSWORD", "admin123")

        # Try to get existing user or create new one
        user, created = User.objects.get_or_create(
            email=email, defaults={"username": username}
        )

        # Always update to ensure superuser status and correct password
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Created admin user: {username} ({email})")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Updated admin user: {username} ({email})")
            )
