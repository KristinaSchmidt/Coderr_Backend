"""Database model for customer reviews of business users."""

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """Store one review per customer and business-user combination."""

    business_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_reviews",
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="written_reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Prevent duplicates and show recently changed reviews first."""

        constraints = [
            models.UniqueConstraint(
                fields=["business_user", "reviewer"],
                name="one_review_per_business",
            )
        ]
        ordering = ["-updated_at"]

    def __str__(self):
        """Return reviewer, business and rating for readable admin data."""
        return f"{self.reviewer} -> {self.business_user}: {self.rating}"
