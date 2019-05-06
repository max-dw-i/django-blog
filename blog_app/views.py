from functools import reduce

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DetailView, FormView, ListView,
                                  View)
from django.views.generic.base import ContextMixin, TemplateView

from .forms import NewCommentForm, SearchForm, SendEmailForm
from .models import Post


class RecentPostsContextMixin(ContextMixin):
    """Mixin for getting context with recent posts"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_posts'] = Post.objects.all().order_by('-publ_date')[:5]
        return context


class PostListView(RecentPostsContextMixin, ListView):
    """View for making main page with the posts list"""
    template_name = 'blog_app/post_list.html'
    context_object_name = 'posts'
    queryset = Post.objects.all().order_by('-publ_date')
    paginate_by = 2


class CommentCreateView(CreateView):
    """View for creating new comments"""
    model = Post
    form_class = NewCommentForm
    template_name = 'blog_app/post.html'

    def get_success_url(self):
        return self.post.get_absolute_url()

    def form_valid(self, form):
        self.post = self.get_object()
        comment = form.save(commit=False)
        # post_id and user in our model are foreignkey fields so we must
        # assign to them not primary key values itself but the objects that
        # have this specific primary key
        comment.post_id = self.post
        # Django pass the user with the request
        comment.user = self.request.user
        comment.save()
        return super().form_valid(form)


class PostDetailView(RecentPostsContextMixin, DetailView):
    """View for rendering post pages (including comments under
    every post) and new comment form
    """
    model = Post
    template_name = 'blog_app/post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context['comments'] = post.post_comments.all()
        context['form'] = NewCommentForm()
        return context


class PostView(View):
    def get(self, request, *args, **kwargs):
        view = PostDetailView.as_view()
        return view(request, *args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        view = CommentCreateView.as_view()
        return view(request, *args, **kwargs)


class ContactFormView(RecentPostsContextMixin, FormView):
    """View for making a contact page and send email to the
    author's blog
    """
    template_name = 'blog_app/contact.html'
    form_class = SendEmailForm
    success_url = reverse_lazy('emailsent')

    def form_valid(self, form):
        send_mail(
            form.cleaned_data['subject'],
            form.cleaned_data['message'],
            form.cleaned_data['email_from'],
            ['email123@mail123.ru'],
            fail_silently=False,
        )
        return super().form_valid(form)


class SearchFormView(RecentPostsContextMixin, FormView):
    """View for searching posts in the blog"""
    template_name = 'blog_app/search.html'
    form_class = SearchForm

    def get_success_url(self):
        url = reverse_lazy(
            'search_result',
            kwargs={'page': 1, 'search_q': self.kwargs['query']}
        )
        return url

    def form_valid(self, form):
        query = form.cleaned_data['query']
        self.kwargs['query'] = '_'.join(query.split(' ')).lower()
        return super().form_valid(form)


class SearchResultListView(RecentPostsContextMixin, ListView):
    """View for the search results"""
    template_name = 'blog_app/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        query = self.kwargs['search_q']
        query_list = query.split('_')
        db_query = reduce(
            lambda x, y: x & y,
            [Q(title__icontains=word) | Q(post_text__icontains=word) for word in query_list]
        )
        posts = Post.objects.filter(db_query).order_by('-publ_date')
        return posts


class AboutView(RecentPostsContextMixin, TemplateView):
    """View for making the about page"""
    template_name = 'blog_app/about.html'


class EmailSentView(RecentPostsContextMixin, TemplateView):
    """View for making the email send success page"""
    template_name = 'blog_app/emailsent.html'


def home(request):
    """View for redirecting from 'home'"""
    return redirect('page', page=1)
