"""Admin configuration for orders."""

from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Display order status and participants in Django admin."""

    list_display = ["id", "title", "customer_user", "business_user", "status"]
    list_filter = ["status", "offer_type"]
    search_fields = ["title", "customer_user__username", "business_user__username"]
