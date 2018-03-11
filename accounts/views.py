from django.contrib.auth import login
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
