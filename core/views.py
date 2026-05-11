from django.shortcuts import render


BEST_MEMBERS = [
    {
        "name": "Ivan. O",
        "profile_path": "#67",
    },
]

COMMON_CONTEXT = {
    'best_members': BEST_MEMBERS,
}


def login(request):
    return render(request, 'core/login.html', COMMON_CONTEXT)


def signup(request):
    return render(request, 'core/signup.html', COMMON_CONTEXT)


def profile(request):
    context = {
        'me': {
            'name': "Ivan. O",
            "profile_path": "#",
            "profile_photo": "https://i.yapx.ru/dkv1w.jpg",
        },
    }
    context.update(**COMMON_CONTEXT)

    return render(request, 'core/profile.html', context)
