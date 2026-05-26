import os
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from .managers import ProfileManager


def profile_photo_path(instance, filename: str) -> str:
    """Generates a dynamic path for profile photos using UUID."""
    extension = os.path.splitext(filename)[-1]
    today_part = timezone.now().strftime('%Y/%m/%d')
    return os.path.join('avatars', today_part, f'{uuid4()}{extension}')


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    photo = models.ImageField(
        upload_to=profile_photo_path,
        default='avatars/default.png',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    answer_cnt = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество ответов'
    )

    objects = ProfileManager()

    def __str__(self):
        return f'Профиль {self.user.username}'

    @property
    def name(self):
        if not self.user.first_name:
            return self.user.username
        return self.user.first_name + \
            (f' {self.user.last_name[0]}.' if self.user.last_name else '')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
