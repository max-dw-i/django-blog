from django.contrib.auth import views as auth_views
from django.urls import path, re_path, include

from accounts import views


urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    # Login is implemented in Django, we don't need to implement our own view
    # function, but we can pass in it the path where to find the template file and
    # add to settings.py 'LOGIN_REDIRECT_URL = 'home''
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    # Logout is implemented in Django so you need to write a logout
    # path and in settings.py assign 'LOGOUT_REDIRECT_URL = 'home''
    path('logout/', auth_views.LogoutView.as_view(next_page='/page/1/'), name='logout'),
]

# Reset passwords
password_reset_view = auth_views.PasswordResetView.as_view(
    template_name='accounts/password_reset.html',
    email_template_name='accounts/password_reset_email.html',
    subject_template_name='accounts/password_reset_subject.txt'
)
password_reset_done_view = auth_views.PasswordResetDoneView.as_view(
    template_name='accounts/password_reset_done.html'
)
password_reset_confirm_view = auth_views.PasswordResetConfirmView.as_view(
    template_name='accounts/password_reset_confirm.html'
)
password_reset_complete_view = auth_views.PasswordResetCompleteView.as_view(
    template_name='accounts/password_reset_complete.html'
)

urlpatterns += [
    path('reset/', include([
        path('', password_reset_view, name='password_reset'),
        path('done/', password_reset_done_view, name='password_reset_done'),
        # if use regular expressions, use re_path() instead of path()
        re_path(
            r'^(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            password_reset_confirm_view,
            name='password_reset_confirm'
        ),
        path('complete/', password_reset_complete_view, name='password_reset_complete'),
    ])),
]

# Change password
password_change_view = auth_views.PasswordChangeView.as_view(
    template_name='accounts/password_change.html',
)
password_change_done_view = auth_views.PasswordChangeDoneView.as_view(
    template_name='accounts/password_change_done.html',
)

urlpatterns += [
    path('settings/', include([
        path('', views.UserUpdateView.as_view(), name='settings'),
        path('password/', password_change_view, name='password_change'),
        path('password/done/', password_change_done_view, name='password_change_done'),
    ])),
]
