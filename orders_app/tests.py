from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import Profile
from offers_app.models import Offer, OfferDetail


class OrderApiTests(APITestCase):
    def setUp(self):
        self.business = User.objects.create_user(username="b", password="x")
        self.customer = User.objects.create_user(username="c", password="x")
        Profile.objects.create(user=self.business, type="business")
        Profile.objects.create(user=self.customer, type="customer")
        offer = Offer.objects.create(user=self.business, title="Offer", description="Desc")
        self.detail = OfferDetail.objects.create(offer=offer,title="Basic",revisions=1,delivery_time_in_days=3,price=100,features=["A"],offer_type="basic")

    def token(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_order_flow(self):
        self.token(self.customer)
        created = self.client.post("/api/orders/", {"offer_detail_id": self.detail.id}, format="json")
        self.assertEqual(created.status_code, 201)
        order_id = created.data["id"]
        self.assertEqual(self.client.get("/api/orders/").status_code, 200)
        self.token(self.business)
        patched = self.client.patch(f"/api/orders/{order_id}/", {"status":"completed"}, format="json")
        self.assertEqual(patched.status_code, 200)
        self.assertEqual(self.client.get(f"/api/completed-order-count/{self.business.id}/").data["order_count"], 1)
        self.assertEqual(self.client.get(f"/api/order-count/{self.business.id}/").data["order_count"], 0)
