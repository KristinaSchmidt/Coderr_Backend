"""Tests for review list, creation, update and deletion endpoints."""

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import Profile


class ReviewApiTests(APITestCase):
    """Verify documented review rules and permissions."""

    def setUp(self):
        self.business = User.objects.create_user(username="business")
        self.customer = User.objects.create_user(username="customer")
        self.other_customer = User.objects.create_user(username="other")
        Profile.objects.create(user=self.business, type=Profile.BUSINESS)
        Profile.objects.create(user=self.customer, type=Profile.CUSTOMER)
        Profile.objects.create(user=self.other_customer, type=Profile.CUSTOMER)

    def auth(self, user):
        """Authenticate the test client as the given user."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def create_review(self):
        """Create one valid review as the primary customer."""
        self.auth(self.customer)
        data = {"business_user": self.business.id, "rating": 5, "description": "Top"}
        return self.client.post("/api/reviews/", data, format="json")

    def test_customer_can_create_review(self):
        response = self.create_review()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["reviewer"], self.customer.id)
        self.assertEqual(response.data["business_user"], self.business.id)

    def test_duplicate_review_returns_400(self):
        self.create_review()
        response = self.client.post(
            "/api/reviews/",
            {"business_user": self.business.id, "rating": 4, "description": "Gut"},
        )
        self.assertEqual(response.status_code, 400)

    def test_business_user_cannot_create_review(self):
        self.auth(self.business)
        response = self.client.post(
            "/api/reviews/",
            {"business_user": self.business.id, "rating": 5, "description": "X"},
        )
        self.assertEqual(response.status_code, 403)

    def test_review_list_filters_and_orders(self):
        self.create_review()
        url = f"/api/reviews/?business_user_id={self.business.id}&ordering=-rating"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["rating"], 5)

    def test_review_owner_can_patch(self):
        created = self.create_review()
        response = self.client.patch(
            f"/api/reviews/{created.data['id']}/",
            {"rating": 4, "description": "Gut"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["rating"], 4)

    def test_other_customer_cannot_patch_or_delete(self):
        created = self.create_review()
        self.auth(self.other_customer)
        url = f"/api/reviews/{created.data['id']}/"
        self.assertEqual(self.client.patch(url, {"rating": 3}).status_code, 403)
        self.assertEqual(self.client.delete(url).status_code, 403)

    def test_owner_can_delete_review(self):
        created = self.create_review()
        response = self.client.delete(f"/api/reviews/{created.data['id']}/")
        self.assertEqual(response.status_code, 204)

    def test_invalid_rating_returns_400(self):
        self.auth(self.customer)
        response = self.client.post(
            "/api/reviews/",
            {"business_user": self.business.id, "rating": 8, "description": "No"},
        )
        self.assertEqual(response.status_code, 400)

    def test_reviews_require_authentication(self):
        response = self.client.get("/api/reviews/")
        self.assertEqual(response.status_code, 401)
