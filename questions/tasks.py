from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
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
        settings.CENTRIFUGO_API_URL,
        api_key=settings.CENTRIFUGO_API_KEY,
        timeout=10
    )
    channel = f"questions:{question_id}"

    request = PublishRequest(channel=channel, data=answer_data)
    client.publish(request)

    return f"Published to {channel}"


@shared_task
def send_notification_email(author_email: str, question_url: str, question_title: str):
    """
    Sends an email notification to the question author.
    """
    subject = f"Новый ответ на твой вопрос! {question_title[:30]}{'...' if len(question_title) > 30 else ''}"
    message = f"Кто то ответил на твой вопрос! {question_title} Посомотреть тут: {question_url}"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [author_email],
        fail_silently=False,
    )
