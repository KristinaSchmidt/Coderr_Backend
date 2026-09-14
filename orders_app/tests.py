"""Tests for order endpoints and order counters."""

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import Profile
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order


class OrderApiTests(APITestCase):
    """Verify customer creation and business status updates."""

    def setUp(self):
        self.business = User.objects.create_user(username="business")
        self.customer = User.objects.create_user(username="customer")
        self.other_business = User.objects.create_user(username="other")
        Profile.objects.create(user=self.business, type=Profile.BUSINESS)
        Profile.objects.create(user=self.customer, type=Profile.CUSTOMER)
        Profile.objects.create(user=self.other_business, type=Profile.BUSINESS)
        offer = Offer.objects.create(user=self.business, title="Offer", description="Desc")
        self.detail = OfferDetail.objects.create(
            offer=offer, title="Logo Design", revisions=3,
            delivery_time_in_days=5, price=150,
            features=["Logo Design", "Visitenkarten"], offer_type="basic"
        )

    def auth(self, user):
        """Authenticate the client as a supplied user."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def create_order(self):
        """Create an order as the customer and return its response."""
        self.auth(self.customer)
        return self.client.post(
            "/api/orders/", {"offer_detail_id": self.detail.id}, format="json"
        )

    def test_customer_can_create_order_snapshot(self):
        response = self.create_order()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["customer_user"], self.customer.id)
        self.assertEqual(response.data["business_user"], self.business.id)
        self.assertEqual(response.data["title"], "Logo Design")
        self.assertEqual(response.data["status"], "in_progress")

    def test_business_cannot_create_order(self):
        self.auth(self.business)
        response = self.client.post(
            "/api/orders/", {"offer_detail_id": self.detail.id}
        )
        self.assertEqual(response.status_code, 403)

    def test_invalid_offer_detail_returns_400(self):
        self.auth(self.customer)
        response = self.client.post("/api/orders/", {"offer_detail_id": 9999})
        self.assertEqual(response.status_code, 400)

    def test_order_list_contains_only_related_orders(self):
        self.create_order()
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_business_owner_can_patch_status(self):
        created = self.create_order()
        self.auth(self.business)
        response = self.client.patch(
            f"/api/orders/{created.data['id']}/",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "completed")

    def test_wrong_business_cannot_patch_order(self):
        created = self.create_order()
        self.auth(self.other_business)
        response = self.client.patch(
            f"/api/orders/{created.data['id']}/", {"status": "completed"}
        )
        self.assertEqual(response.status_code, 403)

    def test_customer_cannot_patch_order(self):
        created = self.create_order()
        response = self.client.patch(
            f"/api/orders/{created.data['id']}/", {"status": "completed"}
        )
        self.assertEqual(response.status_code, 403)

    def test_invalid_status_returns_400(self):
        created = self.create_order()
        self.auth(self.business)
        response = self.client.patch(
            f"/api/orders/{created.data['id']}/", {"status": "invalid"}
        )
        self.assertEqual(response.status_code, 400)

    def test_order_counters_return_expected_counts(self):
        created = self.create_order()
        self.auth(self.business)
        active = self.client.get(f"/api/order-count/{self.business.id}/")
        self.client.patch(
            f"/api/orders/{created.data['id']}/", {"status": Order.COMPLETED}
        )
        completed = self.client.get(
            f"/api/completed-order-count/{self.business.id}/"
        )
        self.assertEqual(active.data["order_count"], 1)
        self.assertEqual(completed.data["completed_order_count"], 1)

    def test_missing_order_returns_404_before_role_check(self):
        """A non-existing order id must return 404, not a permission 403."""
        self.auth(self.customer)
        response = self.client.patch(
            "/api/orders/9999/", {"status": "completed"}, format="json"
        )
        self.assertEqual(response.status_code, 404)

    def test_order_count_unknown_user_returns_404(self):
        """Order count endpoints must reject unknown business user ids."""
        self.auth(self.business)
        response = self.client.get("/api/order-count/9999/")
        self.assertEqual(response.status_code, 404)

    def test_completed_order_count_unknown_user_returns_404(self):
        """Completed count endpoint must reject unknown business user ids."""
        self.auth(self.business)
        response = self.client.get("/api/completed-order-count/9999/")
        self.assertEqual(response.status_code, 404)

