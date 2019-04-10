from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from .. import views


class LogOutTest(TestCase):
    def setUp(self):
        username = 'Vasyan'
        password = '1234567v'
        User.objects.create_user(username, 'vasyan@vasyan.com', password)
        self.client.login(username=username, password=password)

        self.url_page = reverse('page', kwargs={'page': 1})
        self.url_logout = reverse('logout')

    def test_logout_view(self):
        """Tests if the logout link maps LogoutView"""
        view = resolve('/accounts/logout/')
        self.assertEqual(view.func.view_class, views.MyLogoutView)

    def test_after_logout_redirect_home(self):
        """Tests the redirection after logging out"""
        response = self.client.get(self.url_logout)
        self.assertRedirects(response, self.url_page)

    def test_user_is_not_authenticated(self):
        """Tests if the user is not authenticated"""
        self.client.get(self.url_logout)
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
