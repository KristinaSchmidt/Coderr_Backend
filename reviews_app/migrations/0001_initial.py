# Generated for the Coderr project.

from django.conf import settings
from django.core import validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Create the Review model and uniqueness rule."""

    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.PositiveSmallIntegerField(validators=[validators.MinValueValidator(1), validators.MaxValueValidator(5)])),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("business_user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="received_reviews", to=settings.AUTH_USER_MODEL)),
                ("reviewer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="written_reviews", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-updated_at"]},
        ),
        migrations.AddConstraint(
            model_name="review",
            constraint=models.UniqueConstraint(fields=("business_user", "reviewer"), name="one_review_per_business"),
        ),
    ]
