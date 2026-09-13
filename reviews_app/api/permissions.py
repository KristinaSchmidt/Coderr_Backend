"""Custom permissions for review endpoints."""

from rest_framework.permissions import BasePermission

from auth_app.models import Profile


class IsCustomerReviewer(BasePermission):
    """Allow creating reviews only for authenticated customers."""

    def has_permission(self, request, view):
        """Return whether the request user has a customer profile."""
        profile = getattr(request.user, "profile", None)
        return bool(
            request.user.is_authenticated
            and profile
            and profile.type == Profile.CUSTOMER
        )


class IsReviewOwner(BasePermission):
    """Allow changing or deleting only the reviewer's own review."""

    def has_object_permission(self, request, view, obj):
        """Return whether the request user wrote this review."""
        return obj.reviewer == request.user
