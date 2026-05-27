from celery import shared_task
from django.conf import settings
from cent import Client, PublishRequest

from .utils import get_popular_tags, get_best_members


@shared_task
def update_popular_tags():
    tags = get_popular_tags(force_update=True)
    return f"Updated {len(tags)} popular tags"


@shared_task
def update_best_members():
    members = get_best_members(force_update=True)
    return f"Updated {len(members)} best members"


@shared_task
def publish_answer_to_centrifugo(question_id: int, answer_data: dict):
    """
    Publishes a new answer message to the specific question channel in Centrifugo.
    """
    client = Client(
        settings.CENTRIFUGO_URL + "/api",
        api_key=settings.CENTRIFUGO_API_KEY,
        timeout=10
    )
    channel = f"question_{question_id}"

    request = PublishRequest(channel=channel, data=answer_data)
    client.publish(request)

    return f"Published to {channel}"
