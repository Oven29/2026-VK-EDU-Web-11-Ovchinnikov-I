from django.db import models


class QuestionManager(models.Manager):
    def _with_related(self):
        """Приватный метод для базовой настройки QuerySet"""
        return (
            self.get_queryset()
            .select_related('author', 'author__profile')
            .prefetch_related('tags')
            .annotate(answers_count=models.Count('answers', distinct=True))
        )

    def new(self):
        return self._with_related().order_by('-created_at')

    def hot(self):
        return self._with_related().order_by('-rating', '-created_at')

    def by_tag(self, tag_name):
        return self._with_related().filter(tags__name=tag_name).distinct().order_by('-rating')


class TagManager(models.Manager):
    def popular(self):
        return self.annotate(
            question_count=models.Count('questions')
        ).order_by('-question_count')[:10]
