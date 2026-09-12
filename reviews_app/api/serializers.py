from rest_framework import serializers

from auth_app.models import Profile
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.IntegerField(source="reviewer.id", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id", "business_user", "reviewer", "rating", "description",
            "created_at", "updated_at",
        ]
        read_only_fields = ["reviewer", "created_at", "updated_at"]

    def validate_business_user(self, user):
        profile = getattr(user, "profile", None)
        if not profile or profile.type != Profile.BUSINESS:
            raise serializers.ValidationError("The reviewed user must be a business user.")
        return user

    def validate(self, attrs):
        request = self.context.get("request")
        business_user = attrs.get("business_user", getattr(self.instance, "business_user", None))
        if request and business_user == request.user:
            raise serializers.ValidationError("You cannot review yourself.")
        return attrs

    def create(self, validated_data):
        validated_data["reviewer"] = self.context["request"].user
        return super().create(validated_data)
