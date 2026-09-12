from rest_framework.permissions import BasePermission

from auth_app.models import Profile


class IsCustomerReviewer(BasePermission):
    def has_permission(self, request, view):
        profile = getattr(request.user, "profile", None)
        return bool(request.user.is_authenticated and profile and profile.type == Profile.CUSTOMER)


class IsReviewOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user
