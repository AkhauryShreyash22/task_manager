from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Task

User = get_user_model()


class TaskAPITests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="admin123",
            first_name="Admin",
            last_name="User",
            is_staff=True
        )

        self.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="user123",
            first_name="Normal",
            last_name="User",
            is_staff=False
        )

        admin_refresh = RefreshToken.for_user(self.admin)
        self.admin_client = APIClient()
        self.admin_client.cookies["access_token"] = str(admin_refresh.access_token)
        self.admin_client.cookies["refresh_token"] = str(admin_refresh)

        user_refresh = RefreshToken.for_user(self.user)
        self.user_client = APIClient()
        self.user_client.cookies["access_token"] = str(user_refresh.access_token)
        self.user_client.cookies["refresh_token"] = str(user_refresh)

        self.task1 = Task.objects.create(title="Task 1", description="Demo 1", completed=False)
        self.task2 = Task.objects.create(title="Task 2", description="Demo 2", completed=True)

        self.list_url = "/api/tasks/"
        self.detail_url = lambda pk: f"/api/tasks/{pk}/"



    def test_unauthenticated_user_cannot_access_tasks(self):
        client = APIClient()  # No cookies
        response = client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_authenticated_user_can_list_tasks(self):
        response = self.user_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)  # pagination enabled

    def test_list_pagination(self):
        response = self.user_client.get(self.list_url + "?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("results" in response.data)

    def test_filter_by_completed_true(self):
        response = self.user_client.get(self.list_url + "?completed=true")
        self.assertEqual(response.status_code, 200)
        for item in response.data["results"]:
            self.assertTrue(item["completed"])

    def test_filter_by_completed_false(self):
        response = self.user_client.get(self.list_url + "?completed=false")
        self.assertEqual(response.status_code, 200)
        for item in response.data["results"]:
            self.assertFalse(item["completed"])


    def test_user_can_create_task(self):
        payload = {
            "title": "New Task",
            "description": "Created by user",
            "completed": False
        }
        response = self.user_client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "New Task")


    def test_user_can_get_task_detail(self):
        response = self.user_client.get(self.detail_url(self.task1.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.task1.pk)

    

    def test_admin_can_update_task(self):
        payload = {
            "title": "Updated Title",
            "completed": True
        }
        response = self.admin_client.put(self.detail_url(self.task1.pk), payload, format="json")
        self.assertEqual(response.status_code, 200)

        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, "Updated Title")
        self.assertEqual(self.task1.completed, True)

    def test_normal_user_cannot_update_task(self):
        payload = {"title": "User Update Attempt"}
        response = self.user_client.put(self.detail_url(self.task1.pk), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



    def test_admin_can_delete_task(self):
        response = self.admin_client.delete(self.detail_url(self.task2.pk))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(pk=self.task2.pk).exists())

    def test_normal_user_cannot_delete_task(self):
        response = self.user_client.delete(self.detail_url(self.task2.pk))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Task.objects.filter(pk=self.task2.pk).exists())
