from django.core import mail
from django.test import TestCase
from django.urls import resolve, reverse

from ..forms import SendEmailForm
from ..views import ContactView


class ContactPageTests(TestCase):
    def test_contact_page_status_code(self):
        """Tests the about page status code"""
        contact_url = reverse('contact')
        contact_response = self.client.get(contact_url)
        self.assertEquals(contact_response.status_code, 200)

    def test_contact_url_resolves_contact_view(self):
        """Tests resolving ContactView"""
        view = resolve('/contact/')
        self.assertEquals(view.func.view_class, ContactView)


class SendEmailFormTests(TestCase):
    """Tests for the sending emails form"""
    def setUp(self):
        self.contact_url = reverse('contact')
        self.contact_get_response = self.client.get(self.contact_url)

    def test_csrf(self):
        """Test csrf token"""
        self.assertContains(self.contact_get_response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        """Tests if the contact page contains the form"""
        form = self.contact_get_response.context.get('form')
        self.assertIsInstance(form, SendEmailForm)

    def test_form_fields_n_inputs(self):
        """Tests that the form looks like it should"""
        form = SendEmailForm()
        guess_fileds = ['subject', 'email_from', 'message']
        real_fields = list(form.fields)
        self.assertSequenceEqual(guess_fileds, real_fields)
        #content = self.contact_get_response.content
        self.assertContains(self.contact_get_response, '<input', 3)
        self.assertContains(self.contact_get_response, '<textarea')
        self.assertContains(self.contact_get_response, 'type="submit"')


class SendEmailFormValidDataTests(TestCase):
    def setUp(self):
        contact_url = reverse('contact')
        data = {
            'subject': 'Very important letter',
            'email_from': 'vasyan@vasyan.com',
            'message': 'Cho kak?',
        }
        self.email_sent_response = self.client.post(contact_url, data)

    def test_sent_email_redirect(self):
        """Tests the redirection after sending an email"""
        redirect_url = reverse('emailsent')
        self.assertRedirects(self.email_sent_response, redirect_url)

    def test_email_sent(self):
        """Tests if the email has really been sent"""
        self.assertEqual(len(mail.outbox), 1)


class SendEmailFormInvalidDataTests(TestCase):
    def setUp(self):
        self.contact_url = reverse('contact')

    def test_post_empty_fields(self):
        """Tests posting empty fields. Invalid post data should not redirect,
        just render the page again
        """
        data = {'subject': '', 'email_from': '', 'message': ''}
        response = self.client.post(self.contact_url, data)
        self.assertEqual(response.status_code, 200)

    def test_post_empty_fields_form_errors(self):
        """Tests posting empty fields. The expected behavior is to
        show the form again with validation errors
        """
        data = {'subject': '', 'email_from': '', 'message': ''}
        response = self.client.post(self.contact_url, data)
        form = response.context.get('form')
        self.assertTrue(form.errors)

    def test_post_empty_dict(self):
        """Tests posting empty fields. Invalid post data should not redirect,
        just render the page again
        """
        response = self.client.post(self.contact_url, {})
        self.assertEqual(response.status_code, 200)

    def test_post_empty_dict_form_errors(self):
        """Tests posting empty fields. The expected behavior is to
        show the form again with validation errors
        """
        response = self.client.post(self.contact_url, {})
        form = response.context.get('form')
        self.assertTrue(form.errors)

    def test_header_injection(self):
        """Tests the behaviour during header injection attempt. In
        our implementation we check headers during the form validation
        """
        data = {
            'subject': 'Very important letter\nTo:nsa@nsa.com',
            'email_from': 'vasyan@vasyan.com',
            'message': 'Cho kak?',
        }
        response = self.client.post(self.contact_url, data)
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.errors)
