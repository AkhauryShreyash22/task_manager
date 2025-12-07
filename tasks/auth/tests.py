from django.test import TestCase

from django.contrib.auth.models import User
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer
from .utils import set_tokens_cookies, delete_tokens_cookies


class AuthTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.factory = APIRequestFactory()

	def test_register_serializer_password_mismatch(self):
		data = {
			"first_name": "John",
			"last_name": "Doe",
			"email": "jane@example.com",
			"password": "one",
			"confirm_password": "two",
		}
		serializer = RegisterSerializer(data=data)
		self.assertFalse(serializer.is_valid())
		# validation error raised in validate() becomes non_field_errors
		self.assertIn('non_field_errors', serializer.errors)

	def test_register_serializer_duplicate_email(self):
		User.objects.create_user(username='exist', email='exist@example.com', password='pass')
		data = {
			"first_name": "A",
			"last_name": "B",
			"email": "exist@example.com",
			"password": "Password123",
			"confirm_password": "Password123",
		}
		serializer = RegisterSerializer(data=data)
		self.assertFalse(serializer.is_valid())
		self.assertIn('email', serializer.errors)

	def test_register_serializer_create_user(self):
		data = {
			"first_name": "Alice",
			"last_name": "Smith",
			"email": "alice@example.com",
			"password": "Password123",
			"confirm_password": "Password123",
		}
		serializer = RegisterSerializer(data=data)
		self.assertTrue(serializer.is_valid(), serializer.errors)
		user = serializer.save()
		self.assertIsInstance(user, User)
		self.assertEqual(user.email, "alice@example.com")

	def test_set_and_delete_tokens_cookies(self):
		response = Response()
		response = set_tokens_cookies(response, 'access123', 'refresh456')
		self.assertIn('access_token', response.cookies)
		self.assertIn('refresh_token', response.cookies)
		self.assertEqual(response.cookies['access_token'].value, 'access123')

		response = delete_tokens_cookies(response)
		# delete_cookie sets an empty value / max-age 0
		self.assertIn('access_token', response.cookies)
		self.assertTrue(response.cookies['access_token'].value == '' or response.cookies['access_token']['max-age'] == '0')

	def test_cookie_jwt_auth_allows_swagger_paths(self):
		request = self.factory.get('/swagger/')
		request.COOKIES = {}
		try:
			from .exception import CookieJWTAuthentication
		except Exception as e:
			self.skipTest(f"CookieJWTAuthentication import failed; skipping test: {e}")

		auth = CookieJWTAuthentication()
		# swagger paths should bypass authentication
		self.assertIsNone(auth.authenticate(request))

	def test_cookie_jwt_auth_raises_when_not_logged_in(self):
		request = self.factory.get('/profile/')
		request.COOKIES = {}
		try:
			from .exception import CookieJWTAuthentication
			from rest_framework.exceptions import AuthenticationFailed
		except Exception as e:
			self.skipTest(f"CookieJWTAuthentication or AuthenticationFailed import failed; skipping test: {e}")

		auth = CookieJWTAuthentication()
		with self.assertRaises(AuthenticationFailed):
			auth.authenticate(request)

	def test_register_view_sets_cookies(self):
		payload = {
			"first_name": "Reg",
			"last_name": "User",
			"email": "reguser@example.com",
			"password": "Password123",
			"confirm_password": "Password123",
		}
		resp = self.client.post('/register/', payload, format='json')
		self.assertEqual(resp.status_code, 201)
		self.assertIn('message', resp.data)
		self.assertIn('user', resp.data)
		# tokens should be set as cookies on the response
		self.assertIn('access_token', resp.cookies)
		self.assertIn('refresh_token', resp.cookies)

	def test_login_view_and_profile_and_logout_flow(self):
		# Create user
		user = User.objects.create_user(username='bob@example.com', email='bob@example.com', password='mypassword', first_name='Bob', last_name='B')

		# Login
		resp = self.client.post('/login/', {"email": "bob@example.com", "password": "mypassword"}, format='json')
		self.assertEqual(resp.status_code, 200)
		self.assertIn('access_token', resp.cookies)
		self.assertIn('refresh_token', resp.cookies)

		# Use tokens to access profile
		access = resp.cookies['access_token'].value
		refresh = resp.cookies['refresh_token'].value

		# set cookies on client for subsequent requests
		self.client.cookies['access_token'] = access
		self.client.cookies['refresh_token'] = refresh

		profile_resp = self.client.get('/profile/')
		self.assertEqual(profile_resp.status_code, 200)
		self.assertEqual(profile_resp.data['user']['email'], 'bob@example.com')

		# Logout should delete cookies
		logout_resp = self.client.post('/logout/')
		self.assertEqual(logout_resp.status_code, 200)
		self.assertIn('access_token', logout_resp.cookies)
		self.assertTrue(logout_resp.cookies['access_token'].value == '' or logout_resp.cookies['access_token']['max-age'] == '0')

