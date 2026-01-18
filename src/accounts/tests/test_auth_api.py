from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class AccountsAuthAPITests(APITestCase):
    def setUp(self): 
        self.signup_url = "/api/accounts/signup/"
        self.login_url = "/api/accounts/login/"
        self.me_url = "/api/accounts/me/"
        self.logout_url = "/api/accounts/logout/"
        self.refresh_url = "/api/token/refresh/"

        self.user_payload = { # test user data
            "username": "alice",
            "email": "alice@example.com",
            "password": "12345678",
        }

    def test_signup_success(self):
        r = self.client.post(self.signup_url, self.user_payload, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertTrue(r.data["success"])
        self.assertEqual(r.data["data"]["username"], "alice")
        self.assertEqual(r.data["data"]["email"], "alice@example.com")
        self.assertTrue(User.objects.filter(username="alice").exists())

    def test_signup_duplicate_username(self):
        User.objects.create_user(username="alice", email="x@x.com", password="12345678")
        r = self.client.post(self.signup_url, self.user_payload, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.data["success"])
        self.assertIn("username", r.data.get("errors", {}))

    def test_signup_duplicate_email(self):
        User.objects.create_user(username="someone", email="alice@example.com", password="12345678")
        r = self.client.post(self.signup_url, self.user_payload, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.data["success"])
        self.assertIn("email", r.data.get("errors", {}))

    def test_login_success_returns_tokens(self):
        self.client.post(self.signup_url, self.user_payload, format="json")

        r = self.client.post(
            self.login_url,
            {"username": "alice", "password": "12345678"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data["success"])
        self.assertIn("access", r.data["data"])
        self.assertIn("refresh", r.data["data"])

    def test_login_wrong_password(self):
        self.client.post(self.signup_url, self.user_payload, format="json")
        r = self.client.post(
            self.login_url,
            {"username": "alice", "password": "wrongpassword"},
            format="json",
        )
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.data["success"])

    def test_me_requires_auth(self):
        r = self.client.get(self.me_url)
        self.assertEqual(r.status_code, 401)

    def test_me_returns_current_user(self):
        self.client.post(self.signup_url, self.user_payload, format="json")
        login = self.client.post(
            self.login_url, {"username": "alice", "password": "12345678"}, format="json"
        )
        access = login.data["data"]["access"]

        r = self.client.get(self.me_url, HTTP_AUTHORIZATION=f"Bearer {access}")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data["success"])
        self.assertEqual(r.data["data"]["username"], "alice")

    def test_logout_blacklists_refresh_token(self):
        # signup + login
        self.client.post(self.signup_url, self.user_payload, format="json")
        login = self.client.post(
            self.login_url, {"username": "alice", "password": "12345678"}, format="json"
        )
        access = login.data["data"]["access"]
        refresh = login.data["data"]["refresh"]

        # logout (blacklist refresh)
        r = self.client.post(
            self.logout_url,
            {"refresh": refresh},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(r.status_code, 204)

        # refresh should now fail
        rr = self.client.post(self.refresh_url, {"refresh": refresh}, format="json")
        self.assertEqual(rr.status_code, 401)
        self.assertIn("token_not_valid", rr.data.get("code", ""))
