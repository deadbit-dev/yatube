from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_urls_correct_template(self):
        urls_to_template = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for adress, template in urls_to_template.items():
            with self.subTest(adress=adress):
                response = AboutURLTests.guest_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page(self):
        response = AboutURLTests.guest_client.get('unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class AboutViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = AboutViewTests.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
