"""Custom permissions for profile endpoints."""

from rest_framework.permissions import BasePermission


class IsProfileOwner(BasePermission):
    """Allow profile changes only for the profile owner."""

    def has_object_permission(self, request, view, obj):
        """Return whether the authenticated user owns the profile."""
        return obj.user == request.user
