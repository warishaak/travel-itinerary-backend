from django.shortcuts import render
from rest_framework import viewsets
from .models import Itinerary
from .serializers import ItinerarySerializer

class ItineraryViewSet(viewsets.ModelViewSet):

    serializer_class = ItinerarySerializer
    queryset = Itinerary.objects.all()
