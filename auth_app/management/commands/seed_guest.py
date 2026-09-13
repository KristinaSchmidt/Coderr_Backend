"""Management command that creates documented frontend guest users."""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from auth_app.models import Profile


class Command(BaseCommand):
    """Create official guest accounts and optional local test accounts."""

    help = "Create guest and local test users for the Coderr frontend."

    def handle(self, *args, **options):
        """Create every configured guest account idempotently."""
        self.create_guest("andrey", "asdasd", Profile.CUSTOMER)
        self.create_guest("kevin", "asdasd24", Profile.BUSINESS)
        self.create_guest("kristina_customer", "test1234", Profile.CUSTOMER)
        self.create_guest("kristina_business", "test1234", Profile.BUSINESS)
        self.stdout.write(self.style.SUCCESS("Guest users are ready."))

    @staticmethod
    def create_guest(username, password, user_type):
        """Create/update one user, profile and token without duplicates."""
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.com"},
        )
        if created or not user.check_password(password):
            user.set_password(password)
            user.save()
        Profile.objects.update_or_create(user=user, defaults={"type": user_type})
        Token.objects.get_or_create(user=user)
