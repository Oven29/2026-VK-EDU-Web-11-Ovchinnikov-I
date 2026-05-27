from celery import shared_task
from .utils import get_popular_tags, get_best_members


@shared_task
def update_popular_tags():
    tags = get_popular_tags(force_update=True)
    return f"Updated {len(tags)} popular tags"


@shared_task
def update_best_members():
    members = get_best_members(force_update=True)
    return f"Updated {len(members)} best members"
