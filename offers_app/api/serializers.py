from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "id", "title", "revisions", "delivery_time_in_days",
            "price", "features", "offer_type",
        ]

    def validate_features(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("At least one feature is required.")
        return value


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        request = self.context.get("request")
        path = f"/api/offerdetails/{obj.id}/"
        return request.build_absolute_uri(path) if request else path


class OfferSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="user.id", read_only=True)
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id", "user", "title", "image", "description", "created_at",
            "updated_at", "details", "min_price", "min_delivery_time",
            "user_details",
        ]

    def get_min_price(self, obj):
        detail = obj.details.order_by("price").first()
        return detail.price if detail else None

    def get_min_delivery_time(self, obj):
        detail = obj.details.order_by("delivery_time_in_days").first()
        return detail.delivery_time_in_days if detail else None

    def get_user_details(self, obj):
        user = obj.user
        return {
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username,
        }


class OfferWriteSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ["id", "title", "image", "description", "details"]
        read_only_fields = ["id"]

    def validate_details(self, value):
        types = {item["offer_type"] for item in value}
        expected = {OfferDetail.BASIC, OfferDetail.STANDARD, OfferDetail.PREMIUM}
        if len(value) != 3 or types != expected:
            raise serializers.ValidationError("Exactly basic, standard and premium are required.")
        return value

    def create(self, validated_data):
        details = validated_data.pop("details")
        offer = Offer.objects.create(user=self.context["request"].user, **validated_data)
        self.save_details(offer, details)
        return offer

    def update(self, instance, validated_data):
        details = validated_data.pop("details", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if details is not None:
            self.update_details(instance, details)
        return instance

    def save_details(self, offer, details):
        for detail in details:
            OfferDetail.objects.create(offer=offer, **detail)

    def update_details(self, offer, details):
        for detail_data in details:
            offer_type = detail_data.pop("offer_type")
            detail = offer.details.get(offer_type=offer_type)
            for field, value in detail_data.items():
                setattr(detail, field, value)
            detail.save()
