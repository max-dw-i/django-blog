from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from ..forms import SearchForm
from ..models import Post
from ..views import SearchView


class SearchPageTests(TestCase):
    def setUp(self):
        search_url = reverse('search')
        self.search_response = self.client.get(search_url)

    def test_search_page_status_code(self):
        """Tests the search page status code"""
        self.assertEqual(self.search_response.status_code, 200)

    def test_url_resolves_search_view(self):
        """Tests resolving SearchView"""
        view = resolve('/search/')
        self.assertEqual(view.func.view_class, SearchView)


class SearchFormTests(TestCase):
    def setUp(self):
        search_url = reverse('search')
        self.search_response = self.client.get(search_url)

    def test_csrf(self):
        """Test csrf token"""
        self.assertContains(self.search_response, 'csrfmiddlewaretoken')

    def test_search_page_contains_form(self):
        """Tests if the search page contains the search form"""
        form = self.search_response.context.get('form')
        self.assertIsInstance(form, SearchForm)

    def test_form_fields_n_inputs(self):
        """Tests that the form looks like it should"""
        form = SearchForm()
        guess_fields = ['query']
        real_fields = list(form.fields)
        self.assertSequenceEqual(guess_fields, real_fields)
        self.assertContains(self.search_response, '<input', 2)
        self.assertContains(self.search_response, 'type="submit"')


class SearchQueryBaseDataTests(TestCase):
    def setUp(self, data={'query': 'White House'}):
        self.search_url = reverse('search')
        self.search_response = self.client.post(self.search_url, data)
        self.q = '_'.join(data['query'].split(' ')).lower()


class SearchQueryValidDataTests(SearchQueryBaseDataTests):
    def test_redirect_after_new_search(self):
        """Tests the redirection after creation a search query"""
        search_result_url = reverse('search_result', kwargs={'search_q': self.q, 'page': 1})
        self.assertRedirects(self.search_response, search_result_url)


class SearchQueryInvalidDataTests(SearchQueryBaseDataTests):
    def setUp(self):
        super().setUp({'query': ''})

    def test_search_empty(self):
        """Tests posting empty fields. Invalid post data should not redirect,
        just render the page again
        """
        self.assertEqual(self.search_response.status_code, 200)

    def test_search_empty_form_errors(self):
        """Tests posting empty fields. The expected behavior is to
        show the form again with validation errors
        """
        form = self.search_response.context.get('form')
        self.assertTrue(form.errors)
