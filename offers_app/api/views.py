"""Views for offers, offer details and public base information."""

from django.db.models import Avg, Min
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import Profile
from offers_app.models import Offer, OfferDetail
from reviews_app.models import Review
from .pagination import OfferPagination
from .permissions import IsBusinessUser, IsOfferOwner
from .serializers import (
    OfferDetailReadSerializer,
    OfferDetailSerializer,
    OfferListSerializer,
    OfferWriteResponseSerializer,
    OfferWriteSerializer,
)


class OfferListCreateView(generics.ListCreateAPIView):
    """List public offers or create an offer as a business user."""

    pagination_class = OfferPagination
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]

    def get_permissions(self):
        """Keep GET public while restricting POST to business users."""
        if self.request.method == "POST":
            return [IsAuthenticated(), IsBusinessUser()]
        return [AllowAny()]

    def get_serializer_class(self):
        """Choose the write serializer only for POST requests."""
        if self.request.method == "POST":
            return OfferWriteSerializer
        return OfferListSerializer

    def get_queryset(self):
        """Return offers with annotations used by filters and ordering."""
        queryset = Offer.objects.select_related("user").prefetch_related(
            "details"
        ).order_by("id")
        queryset = queryset.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )
        return self._apply_custom_filters(queryset)

    def _apply_custom_filters(self, queryset):
        """Apply creator, minimum-price and delivery-time filters."""
        params = self.request.query_params
        if params.get("creator_id"):
            queryset = queryset.filter(user_id=params["creator_id"])
        if params.get("min_price"):
            queryset = queryset.filter(min_price__gte=params["min_price"])
        if params.get("max_delivery_time"):
            queryset = queryset.filter(
                min_delivery_time__lte=params["max_delivery_time"]
            )
        return queryset.distinct()

    def create(self, request, *args, **kwargs):
        """Create an offer and return complete nested detail objects."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        offer = serializer.save()
        output = OfferWriteResponseSerializer(
            offer,
            context={"request": request},
        )
        return Response(output.data, status=status.HTTP_201_CREATED)


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve an offer or let its owner patch/delete it."""

    queryset = Offer.objects.select_related("user").prefetch_related(
        "details"
    )
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_permissions(self):
        """Require auth for GET and ownership for PATCH/DELETE."""
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOfferOwner()]

    def get_serializer_class(self):
        """Use link details for GET and nested details for PATCH."""
        if self.request.method == "PATCH":
            return OfferWriteSerializer
        return OfferDetailReadSerializer

    def update(self, request, *args, **kwargs):
        """Apply a partial update and return the complete offer details."""
        offer = self.get_object()
        serializer = OfferWriteSerializer(
            offer,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        output = OfferWriteResponseSerializer(offer)
        return Response(output.data, status=status.HTTP_200_OK)


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """Return one complete OfferDetail to authenticated users."""

    queryset = OfferDetail.objects.select_related("offer")
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]


class BaseInfoView(APIView):
    """Return the public counters displayed on the Coderr landing page."""

    permission_classes = [AllowAny]

    def get(self, request):
        """Return offer, review, business and rating statistics."""
        reviews = Review.objects.all()
        average = reviews.aggregate(value=Avg("rating"))["value"] or 0
        data = {
            "review_count": reviews.count(),
            "average_rating": round(float(average), 1),
            "business_profile_count": Profile.objects.filter(
                type=Profile.BUSINESS
            ).count(),
            "offer_count": Offer.objects.count(),
        }
        return Response(data, status=status.HTTP_200_OK)
