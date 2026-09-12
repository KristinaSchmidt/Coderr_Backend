from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import Profile


class ReviewApiTests(APITestCase):
    def setUp(self):
        self.business = User.objects.create_user(username="b2", password="x")
        self.customer = User.objects.create_user(username="c2", password="x")
        Profile.objects.create(user=self.business, type="business")
        Profile.objects.create(user=self.customer, type="customer")
        token = Token.objects.create(user=self.customer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_review_crud(self):
        created = self.client.post("/api/reviews/", {"business_user":self.business.id,"rating":5,"description":"Top"}, format="json")
        self.assertEqual(created.status_code, 201)
        review_id = created.data["id"]
        listed = self.client.get(f"/api/reviews/?business_user_id={self.business.id}&ordering=-updated_at")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data), 1)
        patched = self.client.patch(f"/api/reviews/{review_id}/", {"rating":4,"description":"Gut"}, format="json")
        self.assertEqual(patched.status_code, 200)
        self.assertEqual(self.client.delete(f"/api/reviews/{review_id}/").status_code, 204)
