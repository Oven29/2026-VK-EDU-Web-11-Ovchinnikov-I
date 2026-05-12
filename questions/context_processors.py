from core.models import Profile
from .models import Tag


def sidebar_data(request):
    return {
        'popular_tags': Tag.objects.popular(),
        'best_members': Profile.objects.best(),
    }
