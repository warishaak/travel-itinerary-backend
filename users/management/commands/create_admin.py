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

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f"Admin user {email} already exists, skipping...")
            )
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(
            self.style.SUCCESS(f"✓ Created admin user: {username} ({email})")
        )
