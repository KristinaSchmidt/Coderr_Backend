"""Custom permissions used by offer endpoints."""

from rest_framework.permissions import BasePermission

from auth_app.models import Profile


class IsBusinessUser(BasePermission):
    """Allow the request only for authenticated business users."""

    def has_permission(self, request, view):
        """Return whether the requesting user has a business profile."""
        profile = getattr(request.user, "profile", None)
        return bool(
            request.user.is_authenticated
            and profile
            and profile.type == Profile.BUSINESS
        )


class IsOfferOwner(BasePermission):
    """Allow object changes only for the offer creator."""

    def has_object_permission(self, request, view, obj):
        """Return whether the authenticated user created the offer."""
        return obj.user == request.user
