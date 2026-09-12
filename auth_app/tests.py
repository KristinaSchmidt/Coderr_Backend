from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from auth_app.models import Profile


class AuthApiTests(APITestCase):
    def test_registration_login_and_profile(self):
        data = {"username":"anna","email":"anna@example.com","password":"secret123","repeated_password":"secret123","type":"customer"}
        response = self.client.post("/api/registration/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)
        login = self.client.post("/api/login/", {"username":"anna","password":"secret123"}, format="json")
        self.assertEqual(login.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        user_id = login.data["user_id"]
        profile = self.client.get(f"/api/profile/{user_id}/")
        self.assertEqual(profile.status_code, 200)
        patch = self.client.patch(f"/api/profile/{user_id}/", {"first_name":"Anna","location":"Berlin"}, format="json")
        self.assertEqual(patch.status_code, 200)
        self.assertEqual(patch.data["first_name"], "Anna")

    def test_registration_validation_and_lists(self):
        User.objects.create_user(username="existing", email="x@example.com", password="x")
        bad = self.client.post("/api/registration/", {"username":"existing","email":"new@example.com","password":"a","repeated_password":"b","type":"customer"}, format="json")
        self.assertEqual(bad.status_code, 400)
        owner = User.objects.create_user(username="owner", password="x")
        Profile.objects.create(user=owner, type="business")
        from rest_framework.authtoken.models import Token
        token = Token.objects.create(user=owner)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.assertEqual(self.client.get("/api/profiles/business/").status_code, 200)
        self.assertEqual(self.client.get("/api/profiles/customer/").status_code, 200)
