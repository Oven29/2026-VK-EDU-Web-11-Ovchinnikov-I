from django.db import models
from django.contrib.auth.models import User

from .managers import ProfileManager


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    photo = models.ImageField(
        upload_to='avatars/%Y/%m/%d/',
        default='avatars/default.png',
        blank=True,
        null=True,
        verbose_name='Аватар'
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
