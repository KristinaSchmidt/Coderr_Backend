from django.db.models import Min, Q
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import Profile
from offers_app.models import Offer, OfferDetail
from .pagination import OfferPagination
from .permissions import IsBusinessUser, IsOfferOwner
from .serializers import OfferDetailSerializer, OfferSerializer, OfferWriteSerializer


class OfferListCreateView(generics.ListCreateAPIView):
    pagination_class = OfferPagination
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsBusinessUser()]
        return [AllowAny()]

    def get_serializer_class(self):
        return OfferWriteSerializer if self.request.method == "POST" else OfferSerializer

    def get_queryset(self):
        queryset = Offer.objects.select_related("user").prefetch_related("details")
        queryset = queryset.annotate(min_price=Min("details__price"))
        return self.apply_filters(queryset)

    def apply_filters(self, queryset):
        params = self.request.query_params
        if params.get("creator_id"):
            queryset = queryset.filter(user_id=params["creator_id"])
        if params.get("min_price"):
            queryset = queryset.filter(details__price__gte=params["min_price"])
        if params.get("max_delivery_time"):
            queryset = queryset.filter(details__delivery_time_in_days__lte=params["max_delivery_time"])
        return queryset.distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        offer = serializer.save()
        output = OfferSerializer(offer, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.select_related("user").prefetch_related("details")

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOfferOwner()]

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return OfferWriteSerializer
        return OfferSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = OfferWriteSerializer(instance, data=request.data, partial=partial, context={"request": request})
        serializer.is_valid(raise_exception=True)
        offer = serializer.save()
        return Response(OfferSerializer(offer, context={"request": request}).data)


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.select_related("offer")
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from reviews_app.models import Review
        reviews = Review.objects.all()
        rating = reviews.aggregate(value=Min("rating"))["value"] if reviews.exists() else None
        if reviews.exists():
            rating = round(sum(reviews.values_list("rating", flat=True)) / reviews.count(), 1)
        data = {
            "offer_count": Offer.objects.count(),
            "review_count": reviews.count(),
            "business_profile_count": Profile.objects.filter(type=Profile.BUSINESS).count(),
            "average_rating": rating or 0,
        }
        return Response(data)
