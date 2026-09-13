"""Admin configuration for Coderr user profiles."""

from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Display useful profile information in Django admin."""

    list_display = ["user", "type", "location", "created_at"]
    list_filter = ["type"]
    search_fields = ["user__username", "user__email"]
