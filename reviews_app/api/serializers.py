"""Serializers for customer reviews."""

from rest_framework import serializers

from auth_app.models import Profile
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serialize and validate documented review data."""

    reviewer = serializers.IntegerField(source="reviewer.id", read_only=True)

    class Meta:
        """Define the exact review request/response fields."""

        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["reviewer", "created_at", "updated_at"]

    def validate_business_user(self, user):
        """Require the reviewed account to be a business profile."""
        profile = getattr(user, "profile", None)
        if not profile or profile.type != Profile.BUSINESS:
            raise serializers.ValidationError(
                "The reviewed user must be a business user."
            )
        return user

    def validate(self, attrs):
        """Prevent self-reviews and duplicate customer/business reviews."""
        request = self.context.get("request")
        business = attrs.get("business_user")
        if self.instance is not None:
            business = self.instance.business_user
        if request and business == request.user:
            raise serializers.ValidationError("You cannot review yourself.")
        self._validate_unique_review(request, business)
        return attrs

    def _validate_unique_review(self, request, business):
        """Return HTTP 400 instead of a database error for duplicates."""
        if self.instance or not request or not business:
            return
        exists = Review.objects.filter(
            reviewer=request.user,
            business_user=business,
        ).exists()
        if exists:
            raise serializers.ValidationError(
                "You have already reviewed this business user."
            )

    def create(self, validated_data):
        """Attach the authenticated customer as reviewer."""
        validated_data["reviewer"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Keep reviewer and business fixed while editing review content."""
        validated_data.pop("business_user", None)
        return super().update(instance, validated_data)
