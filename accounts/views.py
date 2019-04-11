from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.views.generic.edit import FormView

from .forms import SignUpForm, UserUpdateForm


class SignUpView(FormView):
    """Sign up view"""

    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('page', kwargs={'page': 1})

    def form_valid(self, form):
        self.success_url = self.request.GET.get('next', SignUpView.success_url)
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    """User info update view"""
    form_class = UserUpdateForm
    template_name = 'accounts/settings.html'
    success_url = reverse_lazy('settings')

    def get_object(self):
        # Get the object we are going to update
        return self.request.user


class MyLoginView(auth_views.LoginView):
    """Login view"""

    template_name = 'accounts/login.html'


class MyLogoutView(auth_views.LogoutView):
    """Logout view"""
    # Logout is implemented in Django so you need to write a logout
    # path and in settings.py assign 'LOGOUT_REDIRECT_URL = 'home''
    next_page = reverse_lazy('page', kwargs={'page': 1})


class MyPasswordResetView(auth_views.PasswordResetView):
    """View rendering the form to fill in email
    to get the link to the password resetting form
    """

    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'


class MyPasswordResetDoneView(auth_views.PasswordResetDoneView):
    """View saying to check the email"""

    template_name = 'accounts/password_reset_done.html'


class MyPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """View rendering the form to set a new password"""

    template_name = 'accounts/password_reset_confirm.html'


class MyPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    """Successful password reset view"""

    template_name = 'accounts/password_reset_complete.html'


class MyPasswordChangeView(auth_views.PasswordChangeView):
    """View rendering the form to change the password"""

    template_name = 'accounts/password_change.html'


class MyPasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    """Successful password change view"""

    template_name = 'accounts/password_change_done.html'
