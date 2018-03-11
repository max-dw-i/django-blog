from django.test import TestCase
from django.urls import resolve, reverse

from ..models import Post
from ..views import PageView


class PageTests(TestCase):
    """page view tests"""
    def setUp(self):
        self.post = Post.objects.create(title='Vasyan', post_text='blog',
                                        before_spoiler='not a good blog')
        self.page_url = reverse('page', kwargs={'page': 1})
        self.page_response = self.client.get(self.page_url)

    def test_page_status_code(self):
        """Tests the page status code"""
        self.assertEqual(self.page_response.status_code, 200)

    def test_page_url_resolves_page_view(self):
        """Tests resolving PageView"""
        view = resolve('/page/1/')
        self.assertEqual(view.func.view_class, PageView)

    def test_page_contains_links_to_posts(self):
        """Tests the page contains the links to the posts"""
        post_url = reverse('post', kwargs={'pk': self.post.pk})
        self.assertContains(self.page_response, 'href="{0}"'.format(post_url))

    def test_outofrange_page(self):
        """Tests if we get 404 when we go to a not existing page"""
        outofrange_page_url = reverse('page', kwargs={'page': 200})
        outofrange_response = self.client.get(outofrange_page_url)
        self.assertEqual(outofrange_response.status_code, 404)

    def test_new_post_appeared_in_center_and_recent_posts(self):
        """Tests if the new post appeared in the navigation bar (recent posts)
        and the main content part (center)
        """
        self.assertContains(self.page_response, 'href="/post/{}/"'.format(self.post.pk), 2)


class Pagination(TestCase):
    def setUp(self):
        self.POSTS_ON_PAGE = 2
        # We wrap every post in a div container, its class name
        self.POST_DIV_CLASS_NAME = 'post'
        for i in range(self.POSTS_ON_PAGE*5+1):
            t = str(i)
            Post.objects.create(title=t, post_text=t, before_spoiler=t)

    def test_page_contains_links_to_other_pages(self):
        """Tests if the page page contains the links to the other pages.
        It must have references at least to the last, first, previous and next
        pages
        """
        page_url = reverse('page', kwargs={'page': 3})
        page_response = self.client.get(page_url)

        # First page
        self.assertContains(
            page_response,
            'href="{}"'.format(reverse('page', kwargs={'page': 1}))
        )
        # Last page
        self.assertContains(
            page_response,
            'href="{}"'.format(reverse('page', kwargs={'page': 6}))
        )
        # Previous page
        self.assertContains(
            page_response,
            'href="{}"'.format(reverse('page', kwargs={'page': 2}))
        )
        # Next page
        self.assertContains(
            page_response,
            'href="{}"'.format(reverse('page', kwargs={'page': 4}))
        )

    def test_every_page_contains_right_number_of_posts(self):
        """Tests every page contains right number of posts"""
        for page in range(1, 6):
            page_url = reverse('page', kwargs={'page': page})
            page_response = self.client.get(page_url)
            self.assertContains(
                page_response,
                'class="{}"'.format(self.POST_DIV_CLASS_NAME),
                self.POSTS_ON_PAGE
            )

        page_url = reverse('page', kwargs={'page': 6})
        page_response = self.client.get(page_url)

        self.assertContains(page_response, 'class="{}"'.format(self.POST_DIV_CLASS_NAME), 1)
