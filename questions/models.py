from django.db import models
from django.contrib.auth.models import User

from .managers import QuestionManager, TagManager


class Tag(models.Model):
    name = models.CharField(max_length=63, unique=True,
                            db_index=True, verbose_name='Название')

    objects = TagManager()

    def __str__(self):
        return f'Тег {self.name}'

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Question(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='questions', verbose_name='Автор')
    tags = models.ManyToManyField(
        Tag, blank=True, related_name='questions', verbose_name='Теги')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания')

    objects = QuestionManager()

    def __str__(self):
        return f'Вопрос {self.title}'

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Answer(models.Model):
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='answers', verbose_name='Автор')
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    is_correct = models.BooleanField(
        default=False, verbose_name='Правильный ответ')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'Ответ на "{self.question.title}" от {self.author.username}'

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
        auto_now_add=True, verbose_name='Дата создания')

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
