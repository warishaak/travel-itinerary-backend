from django.contrib import admin

from .models import Itinerary


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ["title", "destination", "user", "start_date", "end_date"]
    list_filter = ["start_date"]
