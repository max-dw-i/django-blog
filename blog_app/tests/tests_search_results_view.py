from django.test import TestCase
from django.urls import resolve, reverse

from ..models import Post
from ..views import SearchResultListView


class SearchResultBaseDataTests(TestCase):
    def setUp(self, data={'query': 'White House'}):
        Post.objects.create(
            title='HoUSE wHite',
            post_text='oh say can you see',
            before_spoiler='oh say can you see'
        )
        Post.objects.create(
            title='oh say can you see',
            post_text='house WHITE WAS there',
            before_spoiler='house WHITE WAS there'
        )
        Post.objects.create(
            title='White snakes',
            post_text='my houSe is in whatever street',
            before_spoiler='my houSe is in whatever street'
        )
        Post.objects.create(
            title='Green snakes',
            post_text='my houSe is in whatever street',
            before_spoiler='my houSe is in whatever street'
        )
        Post.objects.create(
            title='Red snakes',
            post_text='my car is in whatever street',
            before_spoiler='my houSe is in whatever street'
        )

        # we have recent posts on the left; when we check the search results,
        # we don't want false positive results (we can find our posts title
        # in the nav bar even if they are not in the results); if we create
        # '1' posts after the posts above, we get '1's on the left
        for i in range(100):
            Post.objects.create(title='1', post_text='1', before_spoiler='1')

        q = '_'.join(data['query'].split(' ')).lower()
        self.search_result_url = reverse('search_result', kwargs={'search_q': q, 'page': 1})
        self.search_response = self.client.get(self.search_result_url)


class SearchResultFoundTests(SearchResultBaseDataTests):
    def test_search_page_status_code(self):
        """Tests the search result page status code"""
        self.assertEqual(self.search_response.status_code, 200)

    def test_url_resolves_search_result_view(self):
        """Tests resolving SearchResultListView"""
        view = resolve('/search/vasya/1/')
        self.assertEqual(view.func.view_class, SearchResultListView)

    def test_search_results(self):
        """Tests the result of a search"""
        self.assertContains(self.search_response, '>HoUSE wHite</a>')
        self.assertContains(self.search_response, '>oh say can you see</a>')
        self.assertContains(self.search_response, '>White snakes</a>')
        self.assertNotContains(self.search_response, '>Green snakes</a>')
        self.assertNotContains(self.search_response, '>Red snakes</a>')


class SearchResultNotFoundTests(SearchResultBaseDataTests):
    def setUp(self):
        super().setUp({'query': 'Lady Gaga'})

    def test_search_page_status_code(self):
        """Tests the search result page status code"""
        self.assertEqual(self.search_response.status_code, 200)

    def test_search_results(self):
        """Tests the result of a search"""
        self.assertContains(self.search_response, 'There is no publication')
