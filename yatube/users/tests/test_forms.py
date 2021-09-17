from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_signup(self):
        user_count = User.objects.count()
        from_data = {
            'first_name': 'FirstName',
            'last_name': 'LastName',
            'username': 'NoName',
            'email': 'email@yandex.by',
            'password1': 'Qwe12345678',
            'password2': 'Qwe12345678'
        }
        UserFormTests.guest_client.post(
            reverse('users:signup'),
            data=from_data
        )
        self.assertNotEqual(User.objects.count(), user_count)
