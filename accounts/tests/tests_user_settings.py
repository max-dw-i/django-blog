from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from ..views import UserUpdateView


class UserSettingsPageFormTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='vasyan', email='vasyan@vasyan.com', password='1234567v')
        self.client.login(username='vasyan', password='1234567v')
        settings_url = reverse('settings')
        self.settings_response = self.client.get(settings_url)

    def test_settings_page_status_code(self):
        """Tests if we get the settings page"""
        self.assertEqual(self.settings_response.status_code, 200)

    def test_url_resolves_correct_view(self):
        """Tests if the pwd reset link maps UserUpdateView"""
        view = resolve('/accounts/settings/')
        self.assertEqual(view.func.view_class, UserUpdateView)

    def test_csrf(self):
        """Tests if we get a csrf token"""
        self.assertContains(self.settings_response, 'csrfmiddlewaretoken')

    def test_form_fields_n_inputs(self):
        """Tests if the settings form looks like it should"""
        self.assertContains(self.settings_response, '<input', 4)
        self.assertContains(self.settings_response, 'type="text"', 2)
        self.assertContains(self.settings_response, 'type="email"')
        self.assertContains(self.settings_response, 'name="first_name"')
        self.assertContains(self.settings_response, 'name="last_name"')
        self.assertContains(self.settings_response, 'name="email"')
        self.assertContains(self.settings_response, 'type="submit"')


class SettingsBaseDataTests(TestCase):
    def setUp(self, data = {
            'first_name': 'Kolyan',
            'last_name': 'Kolyan',
            'email': 'kolyan@kolyan.com'
        }):
        User.objects.create_user(username='vasyan', email='vasyan@vasyan.com', password='1234567v')
        self.client.login(username='vasyan', password='1234567v')
        self.settings_url = reverse('settings')
        self.settings_response = self.client.post(self.settings_url, data)


class SettingsWithValidDataTests(SettingsBaseDataTests):
    def test_redirection_to_settings(self):
        """Tests the redirection to the settings page"""
        self.assertRedirects(self.settings_response, self.settings_url)

    def test_user_data_changed(self):
        """Tests the data has been changed"""
        kolyan = User.objects.all().filter(pk=1)[0]
        self.assertEqual(kolyan.first_name, 'Kolyan')
        self.assertEqual(kolyan.last_name, 'Kolyan')
        self.assertEqual(kolyan.email, 'kolyan@kolyan.com')


class SettingsWithInvalidDataTests(SettingsBaseDataTests):
    def setUp(self):
        data = {
            'first_name': '',
            'last_name': '',
            'email': 'kolyan.@kolyan.com'
        }
        super().setUp(data)

    def test_settings_page_invalid_data_status_code(self):
        """Tests the redirection to the password reset done page"""
        self.assertEqual(self.settings_response.status_code, 200)

    def test_form_errors(self):
        """Tests if we get errors after submissioning an invalid form"""
        form = self.settings_response.context.get('form')
        self.assertTrue(form.errors)

    def test_user_data_not_changed(self):
        """Tests the data has not been changed"""
        kolyan = User.objects.all().filter(pk=1)[0]
        self.assertEqual(kolyan.first_name, '')
        self.assertEqual(kolyan.last_name, '')
        self.assertEqual(kolyan.email, 'vasyan@vasyan.com')


class SettingsEmailFieldRequiredTests(SettingsBaseDataTests):
    def setUp(self):
        data = {
            'first_name': '',
            'last_name': '',
            'email': ''
        }
        super().setUp(data)

    def test_form_errors(self):
        """Tests if we get errors after submissioning an invalid form"""
        form = self.settings_response.context.get('form')
        self.assertTrue(form.errors)

    def test_user_data_not_changed(self):
        """Tests the data has not been changed"""
        kolyan = User.objects.all().filter(pk=1)[0]
        self.assertEqual(kolyan.first_name, '')
        self.assertEqual(kolyan.last_name, '')
        self.assertEqual(kolyan.email, 'vasyan@vasyan.com')
