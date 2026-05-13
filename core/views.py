from django.shortcuts import render


def login(request):
    return render(request, 'core/login.html')


def signup(request):
    return render(request, 'core/signup.html')


def profile(request):
    context = {
        'me': {
            'name': "Ivan. O",
            "profile_path": "#",
            "profile_photo": "https://i.yapx.ru/dkv1w.jpg",
        },
    }

    return render(request, 'core/profile.html', context)


def page_not_found(request, exception):
    return render(request, 'errors/404.html', status=404)
