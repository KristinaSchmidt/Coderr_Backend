"""Tests for authentication and profile endpoints."""

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import Profile


class AuthApiTests(APITestCase):
    """Verify documented authentication and profile behaviour."""

    def register(self, username="anna", user_type="customer"):
        """Register and return the API response for a test user."""
        data = {
            "username": username,
            "email": f"{username}@example.com",
            "password": "secret123",
            "repeated_password": "secret123",
            "type": user_type,
        }
        return self.client.post("/api/registration/", data, format="json")

    def authenticate(self, user):
        """Authenticate the test client with a token."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_registration_returns_documented_payload(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["username"], "anna")
        self.assertEqual(response.data["email"], "anna@example.com")
        self.assertIn("token", response.data)
        self.assertIn("user_id", response.data)

    def test_registration_rejects_password_mismatch(self):
        data = {
            "username": "anna", "email": "a@example.com",
            "password": "one", "repeated_password": "two",
            "type": "customer",
        }
        response = self.client.post("/api/registration/", data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_registration_rejects_duplicate_username_and_email(self):
        self.register()
        duplicate = self.register()
        self.assertEqual(duplicate.status_code, 400)

    def test_login_success_and_invalid_credentials(self):
        self.register()
        success = self.client.post(
            "/api/login/", {"username": "anna", "password": "secret123"}
        )
        invalid = self.client.post(
            "/api/login/", {"username": "anna", "password": "wrong"}
        )
        self.assertEqual(success.status_code, 200)
        self.assertEqual(invalid.status_code, 400)

    def test_profile_get_and_patch_updates_user_fields(self):
        response = self.register("business", "business")
        user = User.objects.get(id=response.data["user_id"])
        self.authenticate(user)
        url = f"/api/profile/{user.id}/"
        patch = self.client.patch(
            url,
            {"first_name": "Max", "email": "max@example.com"},
            format="json",
        )
        self.assertEqual(patch.status_code, 200)
        self.assertEqual(patch.data["email"], "max@example.com")
        self.assertIn("created_at", self.client.get(url).data)

    def test_profile_patch_requires_ownership(self):
        owner = User.objects.create_user(username="owner")
        other = User.objects.create_user(username="other")
        Profile.objects.create(user=owner, type=Profile.BUSINESS)
        Profile.objects.create(user=other, type=Profile.CUSTOMER)
        self.authenticate(other)
        response = self.client.patch(
            f"/api/profile/{owner.id}/", {"location": "Berlin"}
        )
        self.assertEqual(response.status_code, 403)

    def test_profile_lists_use_documented_shapes(self):
        business = User.objects.create_user(username="business")
        customer = User.objects.create_user(username="customer")
        Profile.objects.create(user=business, type=Profile.BUSINESS)
        Profile.objects.create(user=customer, type=Profile.CUSTOMER)
        self.authenticate(customer)
        business_data = self.client.get("/api/profiles/business/").data[0]
        customer_data = self.client.get("/api/profiles/customer/").data[0]
        self.assertNotIn("email", business_data)
        self.assertIn("uploaded_at", customer_data)

    def test_profile_endpoints_require_authentication(self):
        user = User.objects.create_user(username="private")
        Profile.objects.create(user=user, type=Profile.CUSTOMER)
        self.assertEqual(self.client.get(f"/api/profile/{user.id}/").status_code, 401)
        self.assertEqual(self.client.get("/api/profiles/business/").status_code, 401)
