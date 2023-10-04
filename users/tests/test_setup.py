from django.urls import reverse
from rest_framework.test import APITestCase

from faker import Faker


class TestSetUp(APITestCase):
    def setUp(self) -> None:
        self.fake = Faker()
        self.register_url = reverse('register')
        self.login_url = reverse('login')

        self.user_data = {
            "username": self.fake.user_name(),
            "email": self.fake.email(),
            "password": self.fake.password()
        }
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
