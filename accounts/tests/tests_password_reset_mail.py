from django.core import mail
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase

class PasswordResetMailTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='vasyan', email='vasyan@vasyan.com', password='1234567p')
        pwd_reset_url = reverse('password_reset')
        data = {
            'email': 'vasyan@vasyan.com',
        }
        self.pwd_reset_response = self.client.post(pwd_reset_url, data)
        self.email = mail.outbox[0]

    def test_email_subject(self):
        """Tests if the email subject looks like it should"""
        self.assertEqual('Please reset your password', self.email.subject)

    def test_email_body(self):
        """Tests the email body"""
        context = self.pwd_reset_response.context
        token = context.get('token')
        uid = context.get('uid')
        password_reset_token_url = reverse('password_reset_confirm', kwargs={
            'uidb64': uid,
            'token': token
        })
        self.assertIn(password_reset_token_url, self.email.body)
        self.assertIn('vasyan', self.email.body)
        self.assertIn('vasyan@vasyan.com', self.email.body)

    def test_email_to(self):
        """Tests if the email recepient is who we need"""
        self.assertEqual(['vasyan@vasyan.com',], self.email.to)
