from django.contrib.auth import get_user_model

from .test_setup import TestSetUp

User = get_user_model()

class TestModels(TestSetUp):

    def test_user_str_method_returns_title(self):
        response = self.client.post(path=self.register_url, data=self.user_data, format="json")
        email = response.data["email"]
        user = User.objects.get(email=email)

        self.assertEqual(str(user), self.user_data["username"])

    def test_creating_new_user_has_is_verified_set_to_false(self):
        response = self.client.post(path=self.register_url, data=self.user_data, format="json")
        email = response.data["email"]
        user = User.objects.get(email=email)

        self.assertFalse(user.is_verified)

    def test_creating_new_user_has_is_active_set_to_true(self):
        response = self.client.post(path=self.register_url, data=self.user_data, format="json")
        email = response.data["email"]
        user = User.objects.get(email=email)

        self.assertTrue(user.is_active)

    def test_user_is_not_assigned_have_admin_or_staff_privileges(self):
        response = self.client.post(path=self.register_url, data=self.user_data, format="json")
        email = response.data["email"]
        user = User.objects.get(email=email)

        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_superuser_has_superuser_privileges_and_enabled_by_default(self):
        superuser = User.objects.create_superuser(**self.user_data)
        
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_verified)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)