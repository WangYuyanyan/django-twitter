from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Tweet


class TweetsAPITest(APITestCase):

    def setUp(self):
        User = get_user_model() # 获取当前使用的用户模型
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        # 登录拿 access token
        #模拟 HTTP POST 请求
        #请求登录接口
        # format="json" 表示发送 JSON 请求体

        response = self.client.post(
            "/api/accounts/login/",
            {
                "username": "testuser",
                "password": "testpass123"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access = response.data["data"]["access"]

    def auth_headers(self):
        return {
            "HTTP_AUTHORIZATION": f"Bearer {self.access}" 
        }

    def test_list_tweets(self):
        response = self.client.get(
            "/api/tweets/",
            **self.auth_headers()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "Tweets list")
        self.assertIsInstance(response.data["data"], list)

    def test_create_tweet(self):
        payload = {
            "content": "hello from test"
        }
        response = self.client.post(
            "/api/tweets/",
            payload,
            format="json",
            **self.auth_headers()
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "Tweet created")
        self.assertEqual(Tweet.objects.count(), 1)
        tweet = Tweet.objects.first()
        self.assertEqual(tweet.user, self.user)
        self.assertEqual(tweet.content, "hello from test")

    def test_create_tweet_with_empty_content(self):
        payload = {
            "content": ""
        }
        response = self.client.post(
            "/api/tweets/",
            payload,
            format="json",
            **self.auth_headers()
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "Validation error")
        self.assertIn("content", response.data["errors"])
    