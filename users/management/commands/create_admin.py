import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "Create a superuser if one does not exist"

    def handle(self, *args, **options):
        email = os.getenv("ADMIN_EMAIL")
        username = os.getenv("ADMIN_USERNAME")
        password = os.getenv("ADMIN_PASSWORD")

        missing_vars = []
        if not email:
            missing_vars.append("ADMIN_EMAIL")
        if not username:
            missing_vars.append("ADMIN_USERNAME")
        if not password:
            missing_vars.append("ADMIN_PASSWORD")

        if missing_vars:
            missing = ", ".join(missing_vars)
            raise CommandError(
                f"Missing required admin environment variables: {missing}. "
                "Refusing to create/update admin with insecure defaults."
            )

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
