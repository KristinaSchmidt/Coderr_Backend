"""Serializers for registration, login and profile endpoints."""

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from auth_app.models import Profile


class RegistrationSerializer(serializers.Serializer):
    """Validate registration data and create a user with profile."""

    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=Profile.TYPE_CHOICES)

    def validate(self, attrs):
        """Ensure both submitted passwords are identical."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return attrs

    def validate_username(self, value):
        """Reject usernames that are already registered."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        """Reject email addresses that are already registered."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data):
        """Create the Django user, matching profile and auth token."""
        user_type = validated_data.pop("type")
        validated_data.pop("repeated_password")
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, type=user_type)
        Token.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """Validate the credentials required by the login endpoint."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ProfileSerializer(serializers.ModelSerializer):
    """Serialize the complete profile used by GET/PATCH profile."""

    user = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    email = serializers.EmailField(source="user.email", required=False)

    class Meta:
        """Define the exact fields from the endpoint documentation."""

        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = ["type", "created_at"]

    def update(self, instance, validated_data):
        """Update Django user fields and the related profile together."""
        user_data = validated_data.pop("user", {})
        self._update_user(instance.user, user_data)
        return super().update(instance, validated_data)

    @staticmethod
    def _update_user(user, user_data):
        """Apply nested user values without storing null strings."""
        for field, value in user_data.items():
            setattr(user, field, value or "")
        if user_data:
            user.save()


class BusinessProfileSerializer(ProfileSerializer):
    """Serialize the compact business profile list response."""

    class Meta(ProfileSerializer.Meta):
        """Expose only fields documented for business profile lists."""

        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]
        read_only_fields = ["type"]


class CustomerProfileSerializer(ProfileSerializer):
    """Serialize the compact customer profile list response."""

    uploaded_at = serializers.DateTimeField(
        source="created_at",
        read_only=True,
    )

    class Meta(ProfileSerializer.Meta):
        """Expose only fields documented for customer profile lists."""

        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "uploaded_at",
            "type",
        ]
        read_only_fields = ["type", "uploaded_at"]
