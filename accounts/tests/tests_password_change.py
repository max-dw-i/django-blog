from django.contrib.auth import views as auth_views
from django.contrib.auth import get_user
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse


class PasswordChangePageFormTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='vasyan', email='vasyan@vasyan.com', password='1234567v')
        self.client.login(username='vasyan', password='1234567v')
        self.pwd_change_url = reverse('password_change')
        self.pwd_change_response = self.client.get(self.pwd_change_url)

    def test_pwd_change_page_status_code(self):
        """Tests if we get the pwd change page"""
        self.assertEqual(self.pwd_change_response.status_code, 200)

    def test_settings_page_contain_password_change_link(self):
        """Tests if the settings page contains the password change link"""
        settings_url = reverse('settings')
        settings_response = self.client.get(settings_url)
        self.assertContains(settings_response, 'href="{}"'.format(self.pwd_change_url))

    def test_url_resolves_correct_view(self):
        """Tests if the pwd change link maps PasswordChangeView"""
        view = resolve('/accounts/settings/password/')
        self.assertEqual(view.func.view_class, auth_views.PasswordChangeView)

    def test_csrf(self):
        """Tests if we get a csrf token"""
        self.assertContains(self.pwd_change_response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        """Tests if the page contains the pwd change form"""
        form = self.pwd_change_response.context.get('form')
        self.assertIsInstance(form, PasswordChangeForm)

    def test_form_fields_n_inputs(self):
        """Tests if the form looks like it should"""
        user = get_user(self.client)
        form = PasswordChangeForm(user)
        expected = ['old_password', 'new_password1', 'new_password2']
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)
        self.assertContains(self.pwd_change_response, '<input', 4)
        self.assertContains(self.pwd_change_response, 'type="password"', 3)
        self.assertContains(self.pwd_change_response, 'type="submit"')


class ChangePasswordAttemptUnauthorizedUser(TestCase):
    def test_redirection_to_login(self):
        """Tests the redirection to the log in page if you want
        to change you password and are not authenticated
        """
        pwd_change_url = reverse('password_change')
        login_url = reverse('login')
        pwd_change_response = self.client.get(pwd_change_url)
        self.assertRedirects(pwd_change_response, '{}?next={}'.format(login_url, pwd_change_url))


class PasswordChangeBaseDataTests(TestCase):
    def setUp(self, data={
            'old_password': 'old_password',
            'new_password1': 'new_password',
            'new_password2': 'new_password',
        }):
        self.user = User.objects.create_user(
            username='vasyan',
            email='vasyan@vasyan.com',
            password='old_password'
        )
        pwd_change_url = reverse('password_change')
        self.client.login(username='vasyan', password='old_password')
        self.response = self.client.post(pwd_change_url, data)


class PasswordChangeWithValidDataTests(PasswordChangeBaseDataTests):
    def test_redirection_to_change_done(self):
        """Tests the redirection to the pwd_change_done page after a
        correct change
        """
        self.assertRedirects(self.response, reverse('password_change_done'))

    def test_password_changed(self):
        """Tests if the password was really changed"""
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password'))

    def test_user_authentication(self):
        """Tests if a user is authenticated after the password change"""
        response = self.client.get(reverse('page', kwargs={'page': 1}))
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class PasswordChangeWithValidInvalidDataTests(PasswordChangeBaseDataTests):
    def setUp(self):
        data = {
            'old_password': '',
            'new_password1': '',
            'new_password2': '',
        }
        super().setUp(data)

    def test_status_code_incorrect_data(self):
        """Tests we get pwd change page if the input data
        is incorrect"""
        self.assertEqual(self.response.status_code, 200)

    def test_form_errors(self):
        """Tests errors appearing"""
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_didnt_change_password(self):
        """Tests if the password wasn't really changed"""
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('old_password'))
