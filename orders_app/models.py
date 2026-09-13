"""Database model for customer orders."""

from django.contrib.auth.models import User
from django.db import models


class Order(models.Model):
    """Store an immutable snapshot of an ordered offer detail."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (IN_PROGRESS, "In progress"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    customer_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="customer_orders",
    )
    business_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="business_orders",
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=IN_PROGRESS,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Show newest orders first."""

        ordering = ["-created_at"]

    def __str__(self):
        """Return a readable order label for the admin area."""
        return f"Order {self.pk}: {self.title}"
