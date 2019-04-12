from django.urls import include, path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('page/<int:page>/', views.PageListView.as_view(), name='page'),
    path('post/<int:pk>/', views.PostNCommentView.as_view(), name='post'),
    path(
        'search/',
        include([
            path('', views.SearchFormView.as_view(), name='search'),
            path(
                '<slug:search_q>/<int:page>/',
                views.SearchResultListView.as_view(),
                name='search_result'
            ),
        ])
    ),
    path('contact/', views.ContactFormView.as_view(), name='contact'),
    path('contact/sent/', views.EmailSentView.as_view(), name='emailsent'),
    path('about/', views.AboutView.as_view(), name='about'),
]
