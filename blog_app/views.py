from functools import reduce

from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, ListView
from django.views.generic.base import ContextMixin, TemplateView

from .forms import NewCommentForm, SearchForm, SendEmailForm
from .models import Post


class RecentPostsContextMixin(ContextMixin):
    """Mixin for getting context with recent posts"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_posts'] = Post.objects.all().order_by('-publ_date')[:5]
        return context


class PageListView(RecentPostsContextMixin, ListView):
    """View for making main page with the posts list"""
    template_name = 'blog_app/page.html'
    context_object_name = 'posts'
    queryset = Post.objects.all().order_by('-publ_date')
    paginate_by = 2


class PostNCommentView(RecentPostsContextMixin, CreateView):
    """View for making separate post pages and posting new comments"""
    template_name = 'blog_app/post.html'
    form_class = NewCommentForm

    def get_success_url(self):
        return reverse_lazy('post', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        comment = form.save(commit=False)
        # post_id and user in our model are foreignkey fields so we must
        # assign to them not primary key values itself but the objects that
        # have this specific primary key
        comment.post_id = post
        # Django pass the user with the request
        comment.user = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        context['post'] = post
        context['comments'] = post.post_comments.all()
        return context


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
    template_name = 'blog_app/page.html'
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
