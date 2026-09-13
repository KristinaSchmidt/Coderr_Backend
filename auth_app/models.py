"""Database models for authentication and user profiles."""

from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Store Coderr-specific information for a Django user."""

    CUSTOMER = "customer"
    BUSINESS = "business"
    TYPE_CHOICES = [(CUSTOMER, "Customer"), (BUSINESS, "Business")]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    file = models.ImageField(upload_to="profiles/", blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    tel = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a readable profile name for the admin area."""
        return f"{self.user.username} ({self.type})"
