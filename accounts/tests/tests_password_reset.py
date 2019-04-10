from django.contrib.auth import get_user
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .. import views


class PasswordResetPageFormTests(TestCase):
    def setUp(self):
        self.pwd_reset_url = reverse('password_reset')
        self.pwd_reset_response = self.client.get(self.pwd_reset_url)

    def test_pwd_reset_page_status_code(self):
        """Tests if we get the pwd reset page"""
        self.assertEqual(self.pwd_reset_response.status_code, 200)

    def test_login_page_contain_pwd_reset_link(self):
        """Tests if login page contains the password reset link"""
        login_url = reverse('login')
        login_response = self.client.get(login_url)
        self.assertContains(login_response, 'href="{}"'.format(self.pwd_reset_url))

    def test_signup_page_contain_pwd_reset_link(self):
        """Tests if signup page contains the password reset link"""
        signup_url = reverse('signup')
        signup_response = self.client.get(signup_url)
        self.assertContains(signup_response, 'href="{}"'.format(self.pwd_reset_url))

    def test_url_resolves_correct_view(self):
        """Tests if the pwd reset link maps PasswordResetView"""
        view = resolve('/accounts/reset/')
        self.assertEqual(view.func.view_class, views.MyPasswordResetView)

    def test_csrf(self):
        """Tests if we get a csrf token"""
        self.assertContains(self.pwd_reset_response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        """Tests if the page contains the pwd reset form"""
        form = self.pwd_reset_response.context.get('form')
        self.assertIsInstance(form, PasswordResetForm)

    def test_form_fields_n_inputs(self):
        """Tests if the form looks like it should"""
        form = PasswordResetForm()
        expected = ['email']
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)
        self.assertContains(self.pwd_reset_response, '<input', 2)
        self.assertContains(self.pwd_reset_response, 'type="email"', 1)
        self.assertContains(self.pwd_reset_response, 'type="submit"')


class PasswordResetWithValidDataTests(TestCase):
    def setUp(self):
        email = 'vasyan@vasyan.com'
        User.objects.create_user(username='vasyan', email=email, password='1234567p')
        pwd_reset_url = reverse('password_reset')
        self.pwd_reset_response = self.client.post(pwd_reset_url, {'email': email})

    def test_redirection_to_pwd_reset_done(self):
        """Tests the redirection to the password reset done page"""
        url = reverse('password_reset_done')
        self.assertRedirects(self.pwd_reset_response, url)

    def test_send_password_reset_email(self):
        """Tests if the password reset email has been sent"""
        self.assertEqual(1, len(mail.outbox))


class PasswordResetWithInvalidDataTests(TestCase):
    def setUp(self):
        pwd_reset_url = reverse('password_reset')
        self.pwd_reset_response = self.client.post(pwd_reset_url, {'email': 'kolyan@vasyan.com'})

    def test_redirection(self):
        """Tests the redirection to the password reset done page"""
        url = reverse('password_reset_done')
        self.assertRedirects(self.pwd_reset_response, url)

    def test_no_reset_email_sent(self):
        """Tests if the password reset email has not been sent"""
        self.assertEqual(0, len(mail.outbox))


class PasswordResetDoneTests(TestCase):
    def setUp(self):
        pwd_reset_done_url = reverse('password_reset_done')
        self.pwd_reset_done_response = self.client.get(pwd_reset_done_url)

    def test_pwd_reset_done_page_status_code(self):
        """Tests if we get the pwd reset done page"""
        self.assertEqual(self.pwd_reset_done_response.status_code, 200)

    def test_url_resolves_correct_view(self):
        """Tests if the pwd reset done link maps PasswordResetDoneView"""
        view = resolve('/accounts/reset/done/')
        self.assertEqual(view.func.view_class, views.MyPasswordResetDoneView)


class PasswordResetConfirmPageFormTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='vasyan', email='vasyan@vasyan.com',
                                        password='1234567v')

        """create a valid password reset token based on how django creates the token internally:
        https://github.com/django/django/blob/1.11.5/django/contrib/auth/forms.py#L280
        """
        self.uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        self.token = default_token_generator.make_token(user)

        pwd_reset_confirm_url = reverse(
            'password_reset_confirm',
            kwargs={'uidb64': self.uid, 'token': self.token}
        )
        self.pwd_reset_confirm_response = self.client.get(pwd_reset_confirm_url, follow=True)

    def test_pwd_reset_confirm_page_status_code(self):
        """Tests if we get the pwd reset confirm page"""
        self.assertEqual(self.pwd_reset_confirm_response.status_code, 200)

    def test_url_resolves_correct_view(self):
        """Tests if the pwd reset done link maps PasswordResetConfirmView"""
        view = resolve('/accounts/reset/{uidb64}/{token}/'.format(uidb64=self.uid, token=self.token))
        self.assertEqual(view.func.view_class, views.MyPasswordResetConfirmView)

    def test_csrf(self):
        """Tests if we get a csrf token"""
        self.assertContains(self.pwd_reset_confirm_response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        """Tests if the page contains the pwd reset confirm form"""
        form = self.pwd_reset_confirm_response.context.get('form')
        self.assertIsInstance(form, SetPasswordForm)

    def test_form_fields_n_inputs(self):
        """Tests if the reset pwd confirm form looks like it should"""
        user = get_user(self.client)
        form = SetPasswordForm(user)
        expected = ['new_password1', 'new_password2']
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)
        self.assertContains(self.pwd_reset_confirm_response, '<input', 3)
        self.assertContains(self.pwd_reset_confirm_response, 'type="password"', 2)
        self.assertContains(self.pwd_reset_confirm_response, 'type="submit"')


class InvalidPasswordResetConfirmTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='vasyan', email='vasyan@vasyan.com',
                                        password='1234567v')
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        token = default_token_generator.make_token(user)

        # Invalidate the token by changing the password
        user.set_password('abcdef123')
        user.save()

        pwd_reset_confirm_url = reverse(
            'password_reset_confirm',
            kwargs={'uidb64': uid, 'token': token}
        )
        self.pwd_reset_confirm_response = self.client.get(pwd_reset_confirm_url)

    def test_pwd_reset_confirm_page_status_code(self):
        """Tests if we get the pwd reset confirm page"""
        self.assertEqual(self.pwd_reset_confirm_response.status_code, 200)

    def test_html(self):
        """Tests the html page we get if we use an invalid password
        reset link
        """
        password_reset_url = reverse('password_reset')
        self.assertContains(self.pwd_reset_confirm_response, 'invalid password reset link')
        self.assertContains(self.pwd_reset_confirm_response, 'href="{0}"'.format(password_reset_url))


class PasswordResetCompleteTests(TestCase):
    def setUp(self):
        pwd_reset_complete_url = reverse('password_reset_complete')
        self.pwd_reset_complete_response = self.client.get(pwd_reset_complete_url)

    def test_pwd_reset_complete_page_status_code(self):
        """Tests if we get the pwd reset complete page"""
        self.assertEqual(self.pwd_reset_complete_response.status_code, 200)

    def test_url_resolves_correct_view(self):
        """Tests if the pwd reset done link maps PasswordResetCompleteView"""
        view = resolve('/accounts/reset/complete/')
        self.assertEqual(view.func.view_class, views.MyPasswordResetCompleteView)
