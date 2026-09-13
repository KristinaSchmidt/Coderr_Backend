"""Views for listing, creating, changing and deleting reviews."""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from reviews_app.models import Review
from .permissions import IsCustomerReviewer, IsReviewOwner
from .serializers import ReviewSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    """List reviews or let authenticated customers create one."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    ordering_fields = ["updated_at", "rating"]

    def get_queryset(self):
        """Apply documented business, reviewer and ordering filters."""
        queryset = Review.objects.select_related(
            "business_user",
            "reviewer",
        )
        queryset = self._apply_id_filters(queryset)
        ordering = self.request.query_params.get("ordering")
        allowed = ["updated_at", "-updated_at", "rating", "-rating"]
        return queryset.order_by(ordering) if ordering in allowed else queryset

    def _apply_id_filters(self, queryset):
        """Filter reviews by optional business and reviewer ids."""
        params = self.request.query_params
        if params.get("business_user_id"):
            queryset = queryset.filter(
                business_user_id=params["business_user_id"]
            )
        if params.get("reviewer_id"):
            queryset = queryset.filter(reviewer_id=params["reviewer_id"])
        return queryset

    def get_permissions(self):
        """Restrict POST to customer profiles while GET needs auth."""
        if self.request.method == "POST":
            return [IsAuthenticated(), IsCustomerReviewer()]
        return [IsAuthenticated()]


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Let a reviewer patch or delete only their own review."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewOwner]
    http_method_names = ["patch", "delete", "head", "options"]
