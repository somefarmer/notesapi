from django.contrib.auth import get_user_model
from rest_framework import status

from .test_setup import TestSetUp

User = get_user_model()

class TestViews(TestSetUp):

    def test_user_cannot_register_without_correct_details(self):
        response = self.client.post(path=self.register_url, data=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_register_with_correct_details(self):
        response = self.client.post(path=self.register_url, data=self.user_data, format="json")
        self.assertEqual(response.data["username"], self.user_data["username"])
        self.assertEqual(response.data["email"], self.user_data["email"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_with_unverified_email_cannot_login(self):
        self.client.post(path=self.register_url, data=self.user_data, format="json")
        response = self.client.post(path=self.login_url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_login_after_verifying_email(self):
        response = self.client.post(path=self.register_url, data=self.user_data, format="json")
        email = response.data["email"]
        user = User.objects.get(email=email)
        user.is_verified = True
        user.save()
        response = self.client.post(path=self.login_url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
