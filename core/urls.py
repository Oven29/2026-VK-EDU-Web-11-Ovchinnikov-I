from django.conf import settings
from django.urls import path, include

from . import views


urlpatterns = [
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
