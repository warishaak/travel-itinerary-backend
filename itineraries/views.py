from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Itinerary
from .serializers import ItinerarySerializer, UserRegistrationSerializer


class ItineraryViewSet(viewsets.ModelViewSet):
    serializer_class = ItinerarySerializer
    queryset = Itinerary.objects.all()


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
