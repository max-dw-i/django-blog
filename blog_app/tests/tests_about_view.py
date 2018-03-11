from django.test import TestCase
from django.urls import resolve, reverse

from ..views import AboutView


class AboutPageTests(TestCase):
    """AboutView tests"""
    about_url = reverse('about')

    def test_resolve_correct_view(self):
        """Tests resolving AboutView"""
        view = resolve('/about/')
        self.assertEqual(view.func.view_class, AboutView)

    def test_about_view_status_code(self):
        """Tests the about page status code"""
        about_response = self.client.get(self.about_url)
        self.assertEqual(about_response.status_code, 200)
