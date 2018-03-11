from django.test import TestCase
from django.urls import resolve, reverse

from ..views import home


class HomeTests(TestCase):
    """home view tests"""
    def test_home_url_resolves_view(self):
        """Tests resolving home view"""
        view = resolve('/')
        self.assertEqual(view.func, home)

    def test_home_view_redirect(self):
        """Tests the redirection from 'home' to '/page/1/'"""
        home_url = reverse('home')
        rederect_url = reverse('page', kwargs={'page': 1})
        response = self.client.get(home_url)
        self.assertRedirects(response, rederect_url)
