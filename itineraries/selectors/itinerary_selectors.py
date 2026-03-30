from itineraries.models import Itinerary


def get_user_itineraries(user):
    return Itinerary.objects.filter(user=user)


def get_public_itineraries():
    return Itinerary.objects.filter(is_public=True)
