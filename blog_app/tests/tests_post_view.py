from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse
from ..forms import NewCommentForm
from ..models import Comment, Post
from ..views import PostView


class PostPageTests(TestCase):
    """Post view tests"""
    def setUp(self):
        Post.objects.create(title='James', post_text='Am I evil?', before_spoiler='Yes, I am')
        self.post_url = reverse('post', kwargs={'pk': 1})
        self.post_response = self.client.get(self.post_url)

    def test_post_page_status_code(self):
        """Tests the post page status code"""
        self.assertEqual(self.post_response.status_code, 200)

    def test_post_view_not_found_status_code(self):
        """Tests the post page status code"""
        url = reverse('post', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_url_resolves_correct_view(self):
        """Tests resolving PostView"""
        view = resolve('/post/1/')
        self.assertEqual(view.func.view_class, PostView)


class NewCommentBaseDataTests(TestCase):
    def setUp(self):
        Post.objects.create(title='Vasyan', post_text='blog', before_spoiler='not a good one')
        User.objects.create_user(username='vasyan', email='vasyan@vasyan.com', password='123')
        self.client.login(username='vasyan', password='123')


class NewCommentFormTests(NewCommentBaseDataTests):
    def setUp(self):
        super().setUp()
        post_url = reverse('post', kwargs={'pk': 1})
        self.post_get_response = self.client.get(post_url)

    def test_csrf(self):
        """Test csrf token"""
        # Check if we get a CSRF token inside the target HTML file
        self.assertContains(self.post_get_response, 'csrfmiddlewaretoken')

    def test_post_page_contains_form(self):
        """Tests if the post page contains the new comment form"""
        form = self.post_get_response.context.get('form')
        self.assertIsInstance(form, NewCommentForm)

    def test_form_fields_n_inputs(self):
        """Tests that the form looks like it should"""
        form = NewCommentForm()
        guess_fields = ['comment_text']
        real_fields = list(form.fields)
        self.assertSequenceEqual(guess_fields, real_fields)
        self.assertContains(self.post_get_response, '<input')
        self.assertContains(self.post_get_response, '<textarea')
        self.assertContains(self.post_get_response, 'type="submit"')


class NewCommentValidDataTests(NewCommentBaseDataTests):
    def setUp(self):
        super().setUp()
        self.post_url = reverse('post', kwargs={'pk': 1})
        data = {'comment_text': 'Viva La Revolucion'}
        self.post_response = self.client.post(self.post_url, data)

    def test_new_comment_created(self):
        """Tests if the new comment is created"""
        self.assertTrue(Comment.objects.exists())

    def test_redirect_after_new_comment(self):
        """Tests the redirection after creation the new comment"""
        self.assertRedirects(self.post_response, self.post_url)

    def test_post_page_contains_new_comment(self):
        """Tests if the post page contains the new comment"""
        response = self.client.get(self.post_url)
        self.assertContains(response, 'Viva La Revolucion')


class NewCommentInvalidDataTests(NewCommentBaseDataTests):
    def setUp(self):
        super().setUp()
        post_url = reverse('post', kwargs={'pk': 1})
        self.post_response = self.client.post(post_url, {'comment_text': ''})

    def test_post_empty(self):
        """Tests posting empty fields. Invalid post data should not redirect,
        just render the page again
        """
        self.assertEqual(self.post_response.status_code, 200)

    def test_post_empty_form_errors(self):
        """Tests posting empty fields. The expected behavior is to
        show the form again with validation errors
        """
        form = self.post_response.context.get('form')
        self.assertTrue(form.errors)

    def test_new_comment_not_created(self):
        """Tests if the new comment is created"""
        self.assertFalse(Comment.objects.exists())


class NewCommentPostWithoutLogin(TestCase):
    def setUp(self):
        Post.objects.create(title='Vasyan', post_text='blog', before_spoiler='not a good one')
        self.post_url = reverse('post', kwargs={'pk': 1})
        data = {'comment_text': 'Viva La Revolucion'}
        self.post_response = self.client.post(self.post_url, data)

    def test_new_comment_created(self):
        """Tests if the new comment is not created"""
        self.assertFalse(Comment.objects.exists())

    def test_redirect_after_new_comment(self):
        """Tests the redirection after creation the new comment"""
        login_url = reverse('login') + '?next={}'.format(self.post_url)
        self.assertRedirects(self.post_response, login_url)

    def test_post_page_contains_new_comment(self):
        """Tests if the post page does not contains the new comment"""
        response = self.client.get(self.post_url)
        self.assertNotContains(response, 'Viva La Revolucion')
