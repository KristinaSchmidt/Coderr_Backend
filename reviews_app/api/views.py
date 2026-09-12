from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from reviews_app.models import Review
from .permissions import IsCustomerReviewer, IsReviewOwner
from .serializers import ReviewSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    ordering_fields = ["updated_at", "rating"]

    def get_queryset(self):
        queryset = Review.objects.select_related("business_user", "reviewer")
        params = self.request.query_params
        if params.get("business_user_id"):
            queryset = queryset.filter(business_user_id=params["business_user_id"])
        if params.get("reviewer_id"):
            queryset = queryset.filter(reviewer_id=params["reviewer_id"])
        ordering = params.get("ordering")
        return queryset.order_by(ordering) if ordering in ["updated_at", "-updated_at", "rating", "-rating"] else queryset

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsCustomerReviewer()]
        return [IsAuthenticated()]


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewOwner]
