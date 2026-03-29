from django.conf import settings
from django.db import models
from django.utils import timezone


class Itinerary(models.Model):
    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="itineraries",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    destination = models.TextField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    is_public = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planning",
        db_index=True,
        help_text="Status of the itinerary (only visible to owner)",
    )
    activities = models.JSONField(default=list, blank=True)
    images = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_auto_status(self):
        """
        Calculate what the status should be based on dates.
        Returns suggested status, but doesn't automatically change it.
        """
        today = timezone.now().date()

        if today < self.start_date:
            # Trip hasn't started yet
            return "planning"
        elif self.start_date <= today <= self.end_date:
            # Trip is currently happening
            return "ongoing"
        elif today > self.end_date:
            # Trip has ended
            return "completed"

        return self.status

    @property
    def is_upcoming(self):
        """Check if trip is in the future."""
        return self.start_date > timezone.now().date()

    @property
    def is_past(self):
        """Check if trip has ended."""
        return self.end_date < timezone.now().date()

    @property
    def is_current(self):
        """Check if trip is currently happening."""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
