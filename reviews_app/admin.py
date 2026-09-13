"""Admin configuration for customer reviews."""

from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Display rating and participants in Django admin."""

    list_display = ["reviewer", "business_user", "rating", "updated_at"]
    list_filter = ["rating"]
    search_fields = ["reviewer__username", "business_user__username"]
