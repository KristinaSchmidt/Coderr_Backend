"""Serializers for order list, creation and status changes."""

from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serialize the complete order snapshot documented by Coderr."""

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        """Expose all documented order response fields."""

        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    """Validate an offer-detail id and create its order snapshot."""

    offer_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=OfferDetail.objects.select_related("offer").all()
    )

    def create(self, validated_data):
        """Create an order from the selected offer detail."""
        detail = validated_data["offer_detail_id"]
        return Order.objects.create(
            customer_user=self.context["request"].user,
            business_user=detail.offer.user,
            **self._snapshot(detail),
        )

    @staticmethod
    def _snapshot(detail):
        """Build immutable detail fields copied into a new order."""
        return {
            "title": detail.title,
            "revisions": detail.revisions,
            "delivery_time_in_days": detail.delivery_time_in_days,
            "price": detail.price,
            "features": list(detail.features),
            "offer_type": detail.offer_type,
        }


class OrderStatusSerializer(serializers.ModelSerializer):
    """Validate the single status field accepted by order PATCH."""

    class Meta:
        """Permit only a documented order status change."""

        model = Order
        fields = ["status"]
