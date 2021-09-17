from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='NoName')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

    def test_urls_uses_correct_template_for_guest(self):
        templates_pages_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_reset'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            # reverse(
            #    'users:password_reset_confirm'
            # ): 'users/password_reset_confirm.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = UserURLTests.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_for_user(self):
        templates_pages_names = {
            reverse('users:logout'): 'users/logged_out.html',
            # reverse(
            #    'users:password_change'
            # ): 'users/password_change_form.html',
            # reverse(
            #    'users:password_change_done'
            # ): 'users/password_change_done.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = UserURLTests.user_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page(self):
        response = UserURLTests.guest_client.get('unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
