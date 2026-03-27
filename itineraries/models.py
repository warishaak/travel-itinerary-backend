from django.conf import settings
from django.db import models


class Itinerary(models.Model):
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
    activities = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
