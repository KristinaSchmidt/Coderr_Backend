"""Admin configuration for offers and their details."""

from django.contrib import admin

from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    """Edit all offer details directly on an offer admin page."""

    model = OfferDetail
    extra = 0


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Display searchable offer data in Django admin."""

    list_display = ["title", "user", "created_at", "updated_at"]
    search_fields = ["title", "user__username"]
    inlines = [OfferDetailInline]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Display service-level data in Django admin."""

    list_display = ["title", "offer", "offer_type", "price"]
    list_filter = ["offer_type"]
