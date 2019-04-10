from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from ..models import Post


class EveryUserLinksTests(TestCase):
    """The links that anonymous and authenticated users must
    be able to see on every page. Since all these links are rendered
    on the base template, we can check any page
    """
    def setUp(self):
        about_url = reverse('about')
        self.response = self.client.get(about_url)

    def test_every_page_contains_link_back_to_home(self):
        """Tests if a user can see the link to the home page"""
        home_url = reverse('home')
        self.assertContains(self.response, 'href="{0}"'.format(home_url))

    def test_every_page_contains_link_to_about(self):
        """Tests if a user can see the link to the about page"""
        about_url = reverse('about')
        self.assertContains(self.response, 'href="{0}"'.format(about_url))

    def test_every_page_contains_link_to_contact(self):
        """Tests if a user can see the link to the contact page"""
        contact_url = reverse('contact')
        self.assertContains(self.response, 'href="{0}"'.format(contact_url))

    def test_every_page_contains_links_to_recent_posts(self):
        """Tests if a user can see the recent posts links"""
        # We render 5 recent pages
        NUM_RECENT_POSTS = 5
        for i in range(NUM_RECENT_POSTS+5):
            t = str(i)
            Post.objects.create(title=t, post_text=t, before_spoiler=t)

        about_url = reverse('about')
        response = self.client.get(about_url)

        posts = Post.objects.all().order_by('-publ_date')
        recents_pks = [post.pk for post in posts[:NUM_RECENT_POSTS]]
        other_pks = [post.pk for post in posts[NUM_RECENT_POSTS:]]

        for pk in recents_pks:
            self.assertContains(response, 'href="/post/{}/"'.format(pk))

        for pk in other_pks:
            self.assertNotContains(response, 'href="/post/{}/"'.format(pk))

        self.assertEqual(len(recents_pks), NUM_RECENT_POSTS)
        self.assertEqual(len(other_pks), 5)


class AnonymousUserLinksTests(TestCase):
    """The links that anonymous users must be able to see on
    every page. Since all these links are rendered on the base
    template, we can check any page
    """
    def setUp(self):
        self.about_url = reverse('about')
        self.response = self.client.get(self.about_url)

    def test_every_page_contains_login_link(self):
        """Tests if every page contains the login link"""
        url_login = reverse('login')
        self.assertContains(self.response, 'href="{}?next={}"'.format(url_login, self.about_url))

    def test_every_page_contains_signup_link(self):
        """Tests if every page contains the signup link"""
        signup_url = reverse('signup')
        self.assertContains(self.response, 'href="{}?next={}"'.format(signup_url, self.about_url))


class AuthenticatedUserLinksTests(TestCase):
    """The links that authenticated users must be able to see on
    every page. Since all these links are rendered on the base
    template, we can check any page
    """
    def setUp(self):
        User.objects.create_user(username='vasyan', email='vasyan@vasyan.com', password='123')
        self.client.login(username='vasyan', password='123')
        about_url = reverse('about')
        self.response = self.client.get(about_url)

    def test_every_page_contains_logout_link(self):
        """Tests if every page contains the logout link"""
        url_logout = reverse('logout')
        self.assertContains(self.response, 'href="{}"'.format(url_logout))

    def test_every_page_contains_settings_link(self):
        """Tests if every page contains the settings link"""
        settings_url = reverse('settings')
        self.assertContains(self.response, 'href="{}"'.format(settings_url))
