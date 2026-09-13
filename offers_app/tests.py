"""Tests for offer, offer-detail and base-info endpoints."""

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import Profile
from offers_app.models import Offer, OfferDetail


class OfferApiTests(APITestCase):
    """Verify the documented offer API including permissions."""

    def setUp(self):
        self.business = User.objects.create_user(
            username="business", first_name="Max", last_name="Mustermann"
        )
        self.customer = User.objects.create_user(username="customer")
        Profile.objects.create(user=self.business, type=Profile.BUSINESS)
        Profile.objects.create(user=self.customer, type=Profile.CUSTOMER)
        self.business_token = Token.objects.create(user=self.business)
        self.customer_token = Token.objects.create(user=self.customer)

    def auth(self, token):
        """Authenticate the client with the supplied token."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    @staticmethod
    def payload(title="Grafikdesign-Paket"):
        """Return the three-detail payload from the documentation."""
        details = [
            {"title": "Basic Design", "revisions": 2, "delivery_time_in_days": 5,
             "price": 100, "features": ["Logo Design"], "offer_type": "basic"},
            {"title": "Standard Design", "revisions": 5, "delivery_time_in_days": 7,
             "price": 200, "features": ["Logo Design"], "offer_type": "standard"},
            {"title": "Premium Design", "revisions": 10, "delivery_time_in_days": 10,
             "price": 500, "features": ["Logo Design"], "offer_type": "premium"},
        ]
        return {"title": title, "image": None, "description": "Grafikdesign",
                "details": details}

    def create_offer(self):
        """Create one valid offer and return its API response."""
        self.auth(self.business_token)
        return self.client.post("/api/offers/", self.payload(), format="json")

    def test_post_offer_returns_complete_details(self):
        response = self.create_offer()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data["details"]), 3)
        self.assertIn("offer_type", response.data["details"][0])
        self.assertNotIn("user", response.data)

    def test_post_offer_requires_business_user(self):
        self.auth(self.customer_token)
        response = self.client.post("/api/offers/", self.payload(), format="json")
        self.assertEqual(response.status_code, 403)

    def test_post_offer_requires_three_unique_complete_details(self):
        self.auth(self.business_token)
        data = self.payload()
        data["details"] = data["details"][:2]
        response = self.client.post("/api/offers/", data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_public_offer_list_is_paginated_with_link_details(self):
        created = self.create_offer()
        self.client.credentials()
        response = self.client.get("/api/offers/?search=Grafikdesign")
        item = response.data["results"][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertIn("url", item["details"][0])
        self.assertIn("user_details", item)
        self.assertEqual(item["id"], created.data["id"])

    def test_single_offer_requires_auth_and_has_no_user_details(self):
        created = self.create_offer()
        self.client.credentials()
        url = f"/api/offers/{created.data['id']}/"
        self.assertEqual(self.client.get(url).status_code, 401)
        self.auth(self.customer_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("user_details", response.data)

    def test_offer_detail_endpoint_returns_complete_object(self):
        created = self.create_offer()
        detail_id = created.data["details"][0]["id"]
        self.auth(self.customer_token)
        response = self.client.get(f"/api/offerdetails/{detail_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["offer_type"], "basic")

    def test_patch_one_detail_preserves_ids(self):
        created = self.create_offer()
        old_ids = [item["id"] for item in created.data["details"]]
        patch = {"title": "Updated", "details": [
            {"offer_type": "basic", "price": 120, "title": "Basic Updated"}
        ]}
        response = self.client.patch(
            f"/api/offers/{created.data['id']}/", patch, format="json"
        )
        new_ids = [item["id"] for item in response.data["details"]]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(old_ids, new_ids)
        self.assertEqual(response.data["title"], "Updated")

    def test_non_owner_cannot_patch_or_delete_offer(self):
        created = self.create_offer()
        self.auth(self.customer_token)
        url = f"/api/offers/{created.data['id']}/"
        self.assertEqual(self.client.patch(url, {"title": "No"}).status_code, 403)
        self.assertEqual(self.client.delete(url).status_code, 403)

    def test_owner_can_delete_offer(self):
        created = self.create_offer()
        response = self.client.delete(f"/api/offers/{created.data['id']}/")
        self.assertEqual(response.status_code, 204)

    def test_offer_filters_use_minimum_values(self):
        self.create_offer()
        self.client.credentials()
        self.assertEqual(self.client.get("/api/offers/?min_price=100").data["count"], 1)
        self.assertEqual(self.client.get("/api/offers/?min_price=150").data["count"], 0)
        self.assertEqual(self.client.get("/api/offers/?max_delivery_time=5").data["count"], 1)

    def test_base_info_is_public(self):
        self.create_offer()
        self.client.credentials()
        response = self.client.get("/api/base-info/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["offer_count"], 1)
