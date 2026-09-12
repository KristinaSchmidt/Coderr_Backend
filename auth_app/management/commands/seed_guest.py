from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from auth_app.models import Profile


class Command(BaseCommand):
    help = "Create guest and local test users for the Coderr frontend."

    def handle(self, *args, **options):
        self.create_guest("andrey", "asdasd", Profile.CUSTOMER)
        self.create_guest("kevin", "asdasd24", Profile.BUSINESS)
        self.create_guest("kristina_customer", "test1234", Profile.CUSTOMER)
        self.create_guest("kristina_business", "test1234", Profile.BUSINESS)
        self.stdout.write(self.style.SUCCESS("Guest users are ready."))

    def create_guest(self, username, password, user_type):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.com"},
        )
        if created or not user.check_password(password):
            user.set_password(password)
            user.save()
        Profile.objects.update_or_create(user=user, defaults={"type": user_type})
        Token.objects.get_or_create(user=user)
