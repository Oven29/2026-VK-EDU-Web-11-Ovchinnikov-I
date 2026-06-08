from datetime import timedelta
from django.utils import timezone
from django.db import models, transaction
from django.db.models import F, Value, OuterRef, Subquery, IntegerField, Sum, Q


class QuestionManager(models.Manager):
    def _with_related(self):
        """Приватный метод для базовой настройки QuerySet"""
        return (
            self.get_queryset()
            .filter(is_active=True)
            .select_related('author', 'author__profile')
            .prefetch_related('tags')
            .annotate(answers_count=models.Count('answers', filter=Q(answers__is_active=True), distinct=True))
        )

    def new(self, user=None):
        return self.with_user_vote(user).order_by('-created_at')

    def hot(self, user=None):
        return self.with_user_vote(user).order_by('-rating', '-created_at')

    def by_tag(self, tag_name, user=None):
        return self.with_user_vote(user).filter(tags__name=tag_name).distinct().order_by('-rating')

    def by_author(self, author_id, user=None):
        """Возвращает вопросы конкретного пользователя"""
        return self.with_user_vote(user).filter(author_id=author_id).order_by('-created_at')

    def with_user_vote(self, user):
        qs = self._with_related()
        if user is None or not user.is_authenticated:
            return qs.annotate(user_vote=Value(0, output_field=IntegerField()))

        from .models import QuestionLike
        vote_subquery = QuestionLike.objects.filter(
            user=user,
            question=OuterRef('pk')
        ).values('value')

        return qs.annotate(user_vote=Subquery(vote_subquery))


class TagManager(models.Manager):
    def popular(self):
        three_months_ago = timezone.now() - timedelta(days=90)
        return self.annotate(
            question_count=models.Count('questions', filter=Q(
                questions__created_at__gte=three_months_ago))
        ).order_by('-question_count')[:10]


class LikeManager(models.Manager):
    @transaction.atomic
    def toggle_vote(self, user, obj, value):
        # Determine if it's QuestionLike or AnswerLike
        lookup_field = 'question' if hasattr(
            self.model, 'question') else 'answer'
        lookup = {lookup_field: obj, 'user': user}

        like, created = self.get_or_create(**lookup, defaults={'value': value})

        if not created:
            if like.value == value:
                # Если нажали на ту же кнопку, убираем голос
                like.value = 0
                like.save()
            else:
                # Если нажали на противоположную кнопку, меняем голос
                like.value = value
                like.save()

        rating_agg = self.filter(
            **{lookup_field: obj}).aggregate(total=Sum('value'))
        obj.rating = rating_agg['total'] or 0
        obj.save(update_fields=['rating'])

        return obj.rating


class AnswerManager(models.Manager):
    def with_user_vote(self, user):
        qs = self.get_queryset().filter(
            is_active=True).select_related('author', 'author__profile')
        if user is None or not user.is_authenticated:
            return qs.annotate(user_vote=Value(0, output_field=IntegerField()))

        from .models import AnswerLike
        vote_subquery = AnswerLike.objects.filter(
            user=user,
            answer=OuterRef('pk')
        ).values('value')

        return qs.annotate(user_vote=Subquery(vote_subquery))

    def get_for_question(self, question, user=None):
        return self.with_user_vote(user).filter(question=question).order_by('-is_correct', '-created_at')

    def toggle_correct(self, user, answer_id):
        # Need to fetch the object here to check permissions
        answer = self.get_queryset().filter(
            is_active=True).select_related('question').get(pk=answer_id)

        if user != answer.question.author:
            return False, 'Not authorized'

        with transaction.atomic():
            if answer.is_correct:
                answer.is_correct = False
                answer.save()
            else:
                answer.question.answers.all().update(is_correct=False)
                answer.is_correct = True
                answer.save()
        return True, answer.is_correct
