from django.db import models


class Itinerary(models.Model):
    title = models.CharField(max_length=200)
    destination = models.TextField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
