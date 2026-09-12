from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import Profile
from offers_app.models import Offer, OfferDetail


class OfferApiTests(APITestCase):
    def setUp(self):
        self.business = User.objects.create_user(username="business", password="x")
        Profile.objects.create(user=self.business, type="business")
        self.token = Token.objects.create(user=self.business)

    def auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def payload(self):
        return {"title":"Webseite","description":"Professionelle Webseite","details":[
            {"title":"Basic","revisions":2,"delivery_time_in_days":5,"price":100,"features":["Logo"],"offer_type":"basic"},
            {"title":"Standard","revisions":5,"delivery_time_in_days":7,"price":200,"features":["Logo","SEO"],"offer_type":"standard"},
            {"title":"Premium","revisions":-1,"delivery_time_in_days":10,"price":500,"features":["Logo","SEO","Support"],"offer_type":"premium"}]}

    def test_offer_crud_and_detail(self):
        self.auth()
        created = self.client.post("/api/offers/", self.payload(), format="json")
        self.assertEqual(created.status_code, 201)
        offer_id = created.data["id"]
        listed = self.client.get("/api/offers/?search=Webseite")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.data["count"], 1)
        detail = self.client.get(created.data["details"][0]["url"].replace("http://testserver", ""))
        self.assertEqual(detail.status_code, 200)
        update = self.payload(); update["title"] = "Neu"
        patched = self.client.patch(f"/api/offers/{offer_id}/", update, format="json")
        self.assertEqual(patched.status_code, 200)
        self.assertEqual(patched.data["title"], "Neu")
        self.assertEqual(self.client.delete(f"/api/offers/{offer_id}/").status_code, 204)

    def test_business_permission_and_validation(self):
        customer = User.objects.create_user(username="customer", password="x")
        Profile.objects.create(user=customer, type="customer")
        token = Token.objects.create(user=customer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.assertEqual(self.client.post("/api/offers/", self.payload(), format="json").status_code, 403)
        self.auth()
        invalid = self.payload(); invalid["details"] = invalid["details"][:2]
        self.assertEqual(self.client.post("/api/offers/", invalid, format="json").status_code, 400)
        self.assertEqual(self.client.get("/api/base-info/").status_code, 200)
