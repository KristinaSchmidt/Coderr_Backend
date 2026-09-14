"""Serializers for offer and offer-detail API responses."""

from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serialize the complete data of one offer detail."""

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        """Expose every documented offer-detail field."""

        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        read_only_fields = ["id"]

    def validate_features(self, value):
        """Require a non-empty list of feature strings."""
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError(
                "At least one feature is required."
            )
        if not all(isinstance(item, str) for item in value):
            raise serializers.ValidationError("Features must be strings.")
        return value




class OfferDetailWriteSerializer(serializers.Serializer):
    """Validate nested detail input for create and partial update."""

    title = serializers.CharField(required=False)
    revisions = serializers.IntegerField(required=False)
    delivery_time_in_days = serializers.IntegerField(min_value=0, required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    features = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
        required=False,
    )
    offer_type = serializers.ChoiceField(choices=OfferDetail.TYPE_CHOICES)

class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Serialize a detail as the id/url pair used by GET offers."""

    url = serializers.SerializerMethodField()

    class Meta:
        """Expose only id and endpoint URL."""

        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        """Return an absolute offer-detail endpoint URL when possible."""
        request = self.context.get("request")
        path = f"/api/offerdetails/{obj.id}/"
        return request.build_absolute_uri(path) if request else path


class OfferReadBaseSerializer(serializers.ModelSerializer):
    """Provide shared read-only fields for offer GET responses."""

    user = serializers.IntegerField(source="user.id", read_only=True)
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        """Define fields common to list and detail responses."""

        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        ]

    def get_min_price(self, obj):
        """Return the lowest price across the offer's three details."""
        detail = obj.details.order_by("price").first()
        return detail.price if detail else None

    def get_min_delivery_time(self, obj):
        """Return the shortest delivery time across all details."""
        detail = obj.details.order_by("delivery_time_in_days").first()
        return detail.delivery_time_in_days if detail else None


class OfferListSerializer(OfferReadBaseSerializer):
    """Serialize one offer inside the paginated public offer list."""

    user_details = serializers.SerializerMethodField()

    class Meta(OfferReadBaseSerializer.Meta):
        """Add creator names required by the list endpoint."""

        fields = OfferReadBaseSerializer.Meta.fields + ["user_details"]

    def get_user_details(self, obj):
        """Return the documented compact creator information."""
        user = obj.user
        return {
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username,
        }


class OfferDetailReadSerializer(OfferReadBaseSerializer):
    """Serialize GET /offers/{id}/ exactly as documented."""


class OfferWriteSerializer(serializers.ModelSerializer):
    """Validate creation and partial changes of offers and details."""

    details = OfferDetailWriteSerializer(many=True, required=True)

    class Meta:
        """Accept only fields that can be created or changed."""

        model = Offer
        fields = ["id", "title", "image", "description", "details"]
        read_only_fields = ["id"]

    def validate_details(self, value):
        """Validate create details and identify every patched detail."""
        types = [item.get("offer_type") for item in value]
        if any(offer_type is None for offer_type in types):
            raise serializers.ValidationError(
                "Each detail must include an offer_type."
            )
        if len(types) != len(set(types)):
            raise serializers.ValidationError("Offer types must be unique.")
        if self.instance is None:
            self._validate_create_details(value, types)
        return value

    @staticmethod
    def _validate_create_details(details, types):
        """Require three complete basic, standard and premium details."""
        expected = {OfferDetail.BASIC, OfferDetail.STANDARD, OfferDetail.PREMIUM}
        required = {
            "title", "revisions", "delivery_time_in_days",
            "price", "features", "offer_type",
        }
        complete = all(required.issubset(detail.keys()) for detail in details)
        if len(types) != 3 or set(types) != expected or not complete:
            raise serializers.ValidationError(
                "Exactly three complete offer details are required."
            )

    def create(self, validated_data):
        """Create the offer for the logged-in business user."""
        details = validated_data.pop("details", [])
        offer = Offer.objects.create(
            user=self.context["request"].user,
            **validated_data,
        )
        self._create_details(offer, details)
        return offer

    def update(self, instance, validated_data):
        """Apply only submitted offer fields and optional detail changes."""
        details = validated_data.pop("details", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if details is not None:
            self._update_details(instance, details)
        return instance

    @staticmethod
    def _create_details(offer, details):
        """Create the three nested detail objects."""
        for detail in details:
            OfferDetail.objects.create(offer=offer, **detail)

    @staticmethod
    def _update_details(offer, details):
        """Update only submitted detail types and preserve their ids."""
        for data in details:
            detail_data = dict(data)
            offer_type = detail_data.pop("offer_type")
            try:
                detail = offer.details.get(offer_type=offer_type)
            except OfferDetail.DoesNotExist as exc:
                raise serializers.ValidationError(
                    {"details": f"Unknown offer_type: {offer_type}."}
                ) from exc
            for field, value in detail_data.items():
                setattr(detail, field, value)
            detail.save()


class OfferWriteResponseSerializer(serializers.ModelSerializer):
    """Serialize POST/PATCH offer responses with complete details."""

    details = OfferDetailSerializer(many=True, read_only=True)

    class Meta:
        """Match the documented create/update success response."""

        model = Offer
        fields = ["id", "title", "image", "description", "details"]
