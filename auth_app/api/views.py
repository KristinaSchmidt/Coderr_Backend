"""Views for Coderr authentication and profile endpoints."""

from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import Profile
from .permissions import IsProfileOwner
from .serializers import (
    BusinessProfileSerializer,
    CustomerProfileSerializer,
    LoginSerializer,
    ProfileSerializer,
    RegistrationSerializer,
)


def auth_payload(user):
    """Build the documented authentication response for a user."""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "username": user.username,
        "email": user.email,
        "user_id": user.id,
    }


class RegistrationView(APIView):
    """Create a customer or business user without authentication."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate registration data and return token information."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(auth_payload(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticate a user and return the existing/new auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Return token data for valid credentials or HTTP 400."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(**serializer.validated_data)
        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(auth_payload(user), status=status.HTTP_200_OK)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve any profile and allow owners to patch their own."""

    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "user_id"
    lookup_url_kwarg = "pk"
    http_method_names = ["get", "patch", "head", "options"]

    def get_permissions(self):
        """Require ownership only when the profile is changed."""
        if self.request.method == "PATCH":
            return [IsAuthenticated(), IsProfileOwner()]
        return [IsAuthenticated()]


class BusinessProfileListView(generics.ListAPIView):
    """Return all business profiles for authenticated users."""

    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Return business profiles together with their Django users."""
        return Profile.objects.filter(
            type=Profile.BUSINESS
        ).select_related("user")


class CustomerProfileListView(generics.ListAPIView):
    """Return all customer profiles for authenticated users."""

    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Return customer profiles together with their Django users."""
        return Profile.objects.filter(
            type=Profile.CUSTOMER
        ).select_related("user")
