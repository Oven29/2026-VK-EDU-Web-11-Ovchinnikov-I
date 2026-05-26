import re

from django.db import models, transaction
from django.contrib.auth.models import User

from .managers import QuestionManager, TagManager, LikeManager, AnswerManager


class DefaultModel(models.Model):
    """Abstract base model with common fields."""

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено в'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано в'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активно?'
    )

    class Meta:
        abstract = True


class Tag(models.Model):
    name = models.CharField(
        max_length=63,
        unique=True,
        db_index=True,
        verbose_name='Название'
    )

    objects = TagManager()

    def __str__(self):
        return re.sub(r'_\d+$', '', self.name)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Question(DefaultModel):
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )
    content = models.TextField(
        max_length=3000,
        verbose_name='Содержание'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='questions',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='questions',
        verbose_name='Теги'
    )
    rating = models.IntegerField(
        default=0,
        verbose_name='Рейтинг'
    )

    objects = QuestionManager()

    def __str__(self):
        return f'Вопрос {self.title}'

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Answer(DefaultModel):
    content = models.TextField(
        max_length=3000,
        verbose_name='Контент'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='answers',
        verbose_name='Автор'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Вопрос'
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name='Правильный ответ'
    )
    rating = models.IntegerField(
        default=0,
        verbose_name='Рейтинг'
    )

    objects = AnswerManager()

    def __str__(self):
        return f'Ответ {self.id}'

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.author_id:
            from core.models import Profile
            profile = Profile.objects.filter(user_id=self.author_id).first()
            if profile:
                profile.sync_answer_cnt()

    @transaction.atomic
    def delete(self, *args, **kwargs):
        author_id = self.author_id
        super().delete(*args, **kwargs)
        if author_id:
            from core.models import Profile
            profile = Profile.objects.filter(user_id=author_id).first()
            if profile:
                profile.sync_answer_cnt()

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'


class LikeAbstract(models.Model):
    LIKE = 1
    DISLIKE = -1
    VOTE_CHOICES = (
        (LIKE, 'Лайк'),
        (DISLIKE, 'Дизлайк'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    value = models.SmallIntegerField(
        choices=VOTE_CHOICES,
        default=LIKE,
        verbose_name='Значение'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    objects = LikeManager()

    class Meta:
        abstract = True


class QuestionLike(LikeAbstract):
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Лайк вопроса'
    )

    class Meta(LikeAbstract.Meta):
        unique_together = ('user', 'question')
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки вопросов'


class AnswerLike(LikeAbstract):
    answer = models.ForeignKey(
        'Answer',
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Лайк ответа'
    )

    class Meta(LikeAbstract.Meta):
        unique_together = ('user', 'answer')
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки ответов'
