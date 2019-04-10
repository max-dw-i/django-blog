from django.contrib.auth import login, views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.views.generic.edit import FormView

from .forms import SignUpForm


class SignUpView(FormView):
    """Sign up view"""

    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('page', kwargs={'page': 1})

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    """User info update view"""

    model = User
    fields = ('first_name', 'last_name', 'email')
    template_name = 'accounts/settings.html'
    success_url = reverse_lazy('settings')

    def get_object(self):
        # Get the object we are going to update
        return self.request.user


class MyLoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'


class MyLogoutView(auth_views.LogoutView):
    # Logout is implemented in Django so you need to write a logout
    # path and in settings.py assign 'LOGOUT_REDIRECT_URL = 'home''
    next_page='/page/1/'


class MyPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'


class MyPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class MyPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'


class MyPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


class MyPasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'accounts/password_change.html'


class MyPasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'
