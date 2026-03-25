from django.contrib import admin

from .models import Itinerary


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ["title", "start_date", "end_date"]
