from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('logout/', views.MyLogoutView.as_view(), name='logout'),
]

# Reset passwords
urlpatterns += [
    path(
        'reset/',
        include([
            path(
                '',
                views.MyPasswordResetView.as_view(),
                name='password_reset'
            ),
            path(
                'done/',
                views.MyPasswordResetDoneView.as_view(),
                name='password_reset_done'
            ),
            # if use regular expressions, use re_path() instead of path()
            re_path(
                r'^(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                views.MyPasswordResetConfirmView.as_view(),
                name='password_reset_confirm'
            ),
            path(
                'complete/',
                views.MyPasswordResetCompleteView.as_view(),
                name='password_reset_complete'
            ),
        ])
    ),
]

# Change password
urlpatterns += [
    path(
        'settings/',
        include([
            path('', views.UserUpdateView.as_view(), name='settings'),
            path(
                'password/',
                views.MyPasswordChangeView.as_view(),
                name='password_change'
            ),
            path(
                'password/done/',
                views.MyPasswordChangeDoneView.as_view(),
                name='password_change_done'
            ),
        ])
    ),
]
