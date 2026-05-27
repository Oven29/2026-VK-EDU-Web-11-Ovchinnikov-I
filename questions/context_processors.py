from django.conf import settings
from .utils import get_popular_tags, get_best_members


def sidebar_data(request):
    return {
        'popular_tags': get_popular_tags(),
        'best_members': get_best_members(),
        'CENTRIFUGO_URL': settings.CENTRIFUGO_URL,
    }
