from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from ..forms import SignUpForm
from ..views import SignUpView


class SignUpFormTest(TestCase):
    def test_form_has_fields(self):
        """Tests if the form contains all the necessary fields"""
        form = SignUpForm()
        expected = ['username', 'email', 'password1', 'password2',]
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)


class SignUpTests(TestCase):
    def setUp(self):
        signup_url = reverse('signup')
        self.signup_response = self.client.get(signup_url)

    def test_signup_status_code(self):
        """Tests if we get the signup page"""
        self.assertEqual(self.signup_response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        """Tests if the login link maps SignUpView"""
        view = resolve('/accounts/signup/')
        self.assertEqual(view.func.view_class, SignUpView)

    def test_csrf(self):
        """Tests if we get a csrf token"""
        self.assertContains(self.signup_response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        """Tests if the page contains the login form"""
        form = self.signup_response.context.get('form')
        self.assertIsInstance(form, SignUpForm)

    def test_form_inputs(self):
        """Tests if the form looks like it should"""
        # csrf, username, email, password1, password2 -> 5 inputs
        self.assertContains(self.signup_response, '<input', 5)
        self.assertContains(self.signup_response, 'type="text"', 1)
        self.assertContains(self.signup_response, 'type="email"', 1)
        self.assertContains(self.signup_response, 'type="password"', 2)
        self.assertContains(self.signup_response, 'type="submit"', 1)

class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        signup_url = reverse('signup')
        data = {
            'username': 'Vasyan',
            'email': 'vasyan@vasyan.com',
            'password1': '1234567v',
            'password2': '1234567v'
        }
        self.signup_response = self.client.post(signup_url, data)
        self.page_url = reverse('page', kwargs={'page': 1})

    def test_redirection(self):
        """Tests the redirect after signing up to /page/1/
        """
        self.assertRedirects(self.signup_response, self.page_url)

    def test_user_creation(self):
        """Tests if the user has been created"""
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self):
        """Tests if a new user is authenticated after signing up"""
        response = self.client.get(self.page_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)

class InvalidSignUpTests(TestCase):
    def setUp(self):
        signup_url = reverse('signup')
        self.signup_response = self.client.post(signup_url, {})

    def test_signup_status_code(self):
        """Tests if an invalid form submission goes to the same page"""
        self.assertEqual(self.signup_response.status_code, 200)

    def test_form_errors(self):
        """Tests if we get errors after submissioning an invalid form"""
        form = self.signup_response.context.get('form')
        self.assertTrue(form.errors)

    def test_dont_create_user(self):
        """Tests if a new user is not created after submissioning
        an invalid form
        """
        self.assertFalse(User.objects.exists())
