from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from friendships.models import Friendship


class FriendshipAPITest(APITestCase):

    def setUp(self):
        self.alice = User.objects.create_user(username='alice', password='pass1234')
        self.bob = User.objects.create_user(username='bob', password='pass1234')
        self.carl = User.objects.create_user(username='carl', password='pass1234')

    def login(self, user):
        response = self.client.post(
            '/api/accounts/login/',
            {'username': user.username, 'password': 'pass1234'},
            format='json',
        )
        token = response.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # ── follow ───────────────────────────────────────────────

    def test_follow_success(self):
        self.login(self.alice)
        response = self.client.post(
            '/api/friendships/follow/',
            {'to_user_id': self.bob.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(Friendship.objects.count(), 1)

    def test_follow_cannot_follow_self(self):
        self.login(self.alice)
        response = self.client.post(
            '/api/friendships/follow/',
            {'to_user_id': self.alice.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_follow_duplicate(self):
        self.login(self.alice)
        self.client.post('/api/friendships/follow/', {'to_user_id': self.bob.id}, format='json')
        response = self.client.post(
            '/api/friendships/follow/',
            {'to_user_id': self.bob.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(Friendship.objects.count(), 1)

    def test_follow_nonexistent_user(self):
        self.login(self.alice)
        response = self.client.post(
            '/api/friendships/follow/',
            {'to_user_id': 99999},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    # ── unfollow ─────────────────────────────────────────────

    def test_unfollow_success(self):
        self.login(self.alice)
        self.client.post('/api/friendships/follow/', {'to_user_id': self.bob.id}, format='json')
        response = self.client.post(
            '/api/friendships/unfollow/',
            {'to_user_id': self.bob.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(Friendship.objects.count(), 0)

    def test_unfollow_not_following(self):
        self.login(self.alice)
        response = self.client.post(
            '/api/friendships/unfollow/',
            {'to_user_id': self.bob.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])

    # ── followers / followings ────────────────────────────────

    def test_followers_list(self):
        # alice 和 carl 都关注了 bob
        Friendship.objects.create(from_user=self.alice, to_user=self.bob)
        Friendship.objects.create(from_user=self.carl, to_user=self.bob)

        self.login(self.alice)
        response = self.client.get(f'/api/friendships/{self.bob.id}/followers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)
        usernames = [item['username'] for item in response.data['data']]
        self.assertIn('alice', usernames)
        self.assertIn('carl', usernames)

    def test_followings_list(self):
        # alice 同时关注了 bob 和 carl
        Friendship.objects.create(from_user=self.alice, to_user=self.bob)
        Friendship.objects.create(from_user=self.alice, to_user=self.carl)

        self.login(self.alice)
        response = self.client.get(f'/api/friendships/{self.alice.id}/followings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)
        usernames = [item['username'] for item in response.data['data']]
        self.assertIn('bob', usernames)
        self.assertIn('carl', usernames)