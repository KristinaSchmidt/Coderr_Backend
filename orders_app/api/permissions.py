"""Custom permissions for order endpoints."""

from rest_framework.permissions import BasePermission

from auth_app.models import Profile


class IsCustomerUser(BasePermission):
    """Allow order creation only for authenticated customers."""

    def has_permission(self, request, view):
        """Return whether the request user has a customer profile."""
        profile = getattr(request.user, "profile", None)
        return bool(
            request.user.is_authenticated
            and profile
            and profile.type == Profile.CUSTOMER
        )


class IsBusinessOrderOwner(BasePermission):
    """Allow order status changes only for the assigned business user."""

    def has_permission(self, request, view):
        """Let object lookup happen before checking business ownership."""
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Allow only the assigned business user to change the order."""
        profile = getattr(request.user, "profile", None)
        return bool(
            profile
            and profile.type == Profile.BUSINESS
            and obj.business_user == request.user
        )
