from django.contrib.auth import get_user, views
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse


class LogInTest(TestCase):
    def setUp(self):
        url_login = reverse('login')
        self.login_response = self.client.get(url_login)

    def test_login_page_status_code(self):
        """Tests if we get the login page"""
        self.assertEqual(self.login_response.status_code, 200)

    def test_url_resolves_correct_view(self):
        """Tests if the login link maps LoginView"""
        view = resolve('/accounts/login/')
        self.assertEqual(view.func.view_class, views.LoginView)

    def test_contains_form(self):
        """Tests if the page contains the login form"""
        form = self.login_response.context.get('form')
        self.assertIsInstance(form, AuthenticationForm)

    def test_form_fields_n_inputs(self):
        """Tests if the form looks like it should"""
        form = AuthenticationForm()
        expected = ['username', 'password']
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)
        # csrf, username, password -> 3 inputs
        self.assertContains(self.login_response, '<input', 3)
        self.assertContains(self.login_response, 'type="text"', 1)
        self.assertContains(self.login_response, 'type="password"', 1)
        self.assertContains(self.login_response, 'type="submit"')

    def test_csrf(self):
        """Tests if we get a csrf token"""
        self.assertContains(self.login_response, 'csrfmiddlewaretoken')


class LoginBaseDataTests(TestCase):
    def setUp(self, data={'username': 'Vasyan', 'password': '1234567v'}):
        User.objects.create_user('Vasyan', 'vasyan@vasyan.com', '1234567v')
        url_login = reverse('login')
        url = url_login + '?next=/page/1/'
        self.login_response = self.client.post(url, data)

class LoginValidDataTests(LoginBaseDataTests):
    def test_redirect_to_same_page_after_login(self):
        """Tests the redirection after logging in with
        valid data
        """
        url_page = reverse('page', kwargs={'page': 1})
        self.assertRedirects(self.login_response, url_page)

    def test_user_is_authenticated(self):
        """Tests if the user is authenticated"""
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

class LoginInvalidDataTests(LoginBaseDataTests):
    def setUp(self):
        # There is no such a user in the db
        data = {
            'username': 'Petya',
            'password': '1234567p',
        }
        super().setUp(data=data)

    def test_page_status_code_after_login(self):
        """Tests the redirection after logging in with
        invalid data
        """
        self.assertEqual(self.login_response.status_code, 200)

    def test_form_errors(self):
        """Tests getting errors after logging in with
        invalid data
        """
        form = self.login_response.context.get('form')
        self.assertTrue(form.errors)

    def test_user_is_not_authenticated(self):
        """Tests if the user is not authenticated"""
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
