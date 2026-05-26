from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from django.views.generic import CreateView, UpdateView, View
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy

from .forms import LoginForm, SignupForm, SettingsForm


class LoginView(DjangoLoginView):
    form_class = LoginForm
    template_name = 'core/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '')
        return context


class SignupView(UserPassesTestMixin, CreateView):
    form_class = SignupForm
    template_name = 'core/signup.html'
    success_url = reverse_lazy('index')

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('index')

    def form_valid(self, form):
        response = super().form_valid(form)
        auth.login(self.request, self.object)
        return response


class LogoutView(View):
    def get(self, request):
        auth.logout(request)
        return redirect('index')


@method_decorator(login_required, name='dispatch')
class SettingsView(UpdateView):
    form_class = SettingsForm
    template_name = 'core/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user


def page_not_found(request, exception):
    return render(request, 'errors/404.html', status=404)
