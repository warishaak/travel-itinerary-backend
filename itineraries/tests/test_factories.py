from datetime import date, timedelta

from itineraries.models import Itinerary


class ItineraryFactory:

    @staticmethod
    def build_valid_itinerary_data(**kwargs):
        default_data = {
            "title": "Default Test Trip",
            "destination": "Test Destination",
            "start_date": date.today() + timedelta(days=30),
            "end_date": date.today() + timedelta(days=35),
        }
        default_data.update(kwargs)
        return default_data

    @staticmethod
    def create_itinerary(**kwargs):
        data = ItineraryFactory.build_valid_itinerary_data(**kwargs)
        return Itinerary.objects.create(**data)

    @staticmethod
    def create_multiple_itineraries(count=3, **kwargs):
        itineraries = []
        for i in range(count):
            data = kwargs.copy()
            data.setdefault("title", f"Trip {i + 1}")
            data.setdefault("destination", f"Destination {i + 1}")
            data.setdefault("start_date", date.today() + timedelta(days=i * 7))
            data.setdefault("end_date", date.today() + timedelta(days=i * 7 + 5))

            itinerary = ItineraryFactory.create_itinerary(**data)
            itineraries.append(itinerary)

        return itineraries

    @staticmethod
    def build_invalid_date_range_data():
        return {
            "title": "Invalid Date Range Trip",
            "destination": "Test Destination",
            "start_date": date.today() + timedelta(days=10),
            "end_date": date.today() + timedelta(days=5),
        }

    @staticmethod
    def build_same_day_itinerary_data():
        trip_date = date.today() + timedelta(days=15)
        return {
            "title": "Day Trip",
            "destination": "Nearby City",
            "start_date": trip_date,
            "end_date": trip_date,
        }

    @staticmethod
    def build_long_title_data(length=200):
        return {
            "title": "A" * length,
            "destination": "Test Destination",
            "start_date": date.today() + timedelta(days=20),
            "end_date": date.today() + timedelta(days=25),
        }
