from django.test import TestCase
from django.urls import resolve, reverse

from ..views import EmailSentView


class EmailSentPageTests(TestCase):
    def test_sent_page_status_code(self):
        """Tests the email sent page status code"""
        email_sent_url = reverse('emailsent')
        email_sent_response = self.client.get(email_sent_url)
        self.assertEqual(email_sent_response.status_code, 200)

    def test_email_sent_url_resolves_emailsentview(self):
        """Tests resolving EnailSentView"""
        view = resolve('/contact/sent/')
        self.assertEqual(view.func.view_class, EmailSentView)
