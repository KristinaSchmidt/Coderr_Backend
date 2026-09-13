"""Database models for offers and their three service levels."""

from django.contrib.auth.models import User
from django.db import models


class Offer(models.Model):
    """Store an offer created by a business user."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="offers",
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="offers/", blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Show the most recently changed offers first."""

        ordering = ["-updated_at"]

    def __str__(self):
        """Return the offer title for readable admin entries."""
        return self.title


class OfferDetail(models.Model):
    """Store one basic, standard or premium detail of an offer."""

    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    TYPE_CHOICES = [
        (BASIC, "Basic"),
        (STANDARD, "Standard"),
        (PREMIUM, "Premium"),
    ]

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="details",
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    class Meta:
        """Keep one detail per type and order details by price."""

        constraints = [
            models.UniqueConstraint(
                fields=["offer", "offer_type"],
                name="unique_offer_type",
            )
        ]
        ordering = ["price"]

    def __str__(self):
        """Return offer and service level for the admin area."""
        return f"{self.offer.title} - {self.offer_type}"
