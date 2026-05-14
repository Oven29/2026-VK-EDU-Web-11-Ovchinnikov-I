from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from .forms import LoginForm, SignupForm, SettingsForm


def login(request):
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)

            redirect_to = request.POST.get('next', '')
            if not url_has_allowed_host_and_scheme(
                url=redirect_to,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                redirect_to = settings.LOGIN_REDIRECT_URL
            return redirect(redirect_to)

    else:
        form = LoginForm()

    context = {
        'form': form,
        'next': next_url,
    }

    return render(request, 'core/login.html', context)


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)

    else:
        form = SignupForm()

    context = {'form': form}

    return render(request, 'core/signup.html', context)


def logout(request):
    auth.logout(request)
    next_page = request.META.get('HTTP_REFERER', settings.LOGIN_REDIRECT_URL)

    return redirect(next_page)


@login_required
def profile(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')

    else:
        form = SettingsForm(instance=request.user)

    context = {'form': form}

    return render(request, 'core/profile.html', context)


def page_not_found(request, exception):
    return render(request, 'errors/404.html', status=404)
