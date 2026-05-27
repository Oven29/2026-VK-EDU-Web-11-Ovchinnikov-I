import jwt
import time
from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from core.templatetags.core_tags import name_filter
from core.models import Profile
from questions.models import Tag

CACHE_KEY_POPULAR_TAGS = 'popular_tags'
CACHE_KEY_BEST_MEMBERS = 'best_members'
CACHE_TIMEOUT = 3600 * 24


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)

    page_num = request.GET.get('page', 1)

    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(1)

    return page


def get_popular_tags(force_update=False):
    data = None if force_update else cache.get(CACHE_KEY_POPULAR_TAGS)
    if data is None:
        data = list(Tag.objects.popular().values('id', 'name'))
        cache.set(CACHE_KEY_POPULAR_TAGS, data, CACHE_TIMEOUT)
    return data


def get_best_members(force_update=False):
    data = None if force_update else cache.get(CACHE_KEY_BEST_MEMBERS)
    if data is None:
        profiles = Profile.objects.best()
        data = []
        for profile in profiles:
            data.append({
                'name': name_filter(profile.user),
                'username': profile.user.username,
            })
        cache.set(CACHE_KEY_BEST_MEMBERS, data, CACHE_TIMEOUT)
    return data


def get_centrifugo_token(user_id: str) -> str:
    """
    Generates a JWT token for Centrifugo connection authentication.
    """
    claims = {
        "sub": str(user_id),
        "exp": int(time.time()) + 3600 * 24  # Token valid for 24 hours
    }
    return jwt.encode(claims, settings.CENTRIFUGO_SECRET, algorithm="HS256")
