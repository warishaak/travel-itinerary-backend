from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserSerializer, UserUpdateSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = ()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"id": user.id, "email": user.email, "message": "User created successfully"},
            status=status.HTTP_201_CREATED,
        )


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Protected endpoint to get and update the currently authenticated user."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user
