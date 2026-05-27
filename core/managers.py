from datetime import timedelta
from django.db import models
from django.db.models import Sum, Q, Subquery, OuterRef, IntegerField
from django.db.models.functions import Coalesce
from django.utils import timezone


class ProfileManager(models.Manager):
    def best(self):
        one_week_ago = timezone.now() - timedelta(days=7)
        from questions.models import Question, Answer

        question_rating = Question.objects.filter(
            author=OuterRef('user'),
            is_active=True,
            created_at__gte=one_week_ago
        ).values('author').annotate(total=Sum('rating')).values('total')

        answer_rating = Answer.objects.filter(
            author=OuterRef('user'),
            is_active=True,
            created_at__gte=one_week_ago
        ).values('author').annotate(total=Sum('rating')).values('total')

        return self.select_related('user').annotate(
            week_rating=Coalesce(Subquery(question_rating, output_field=IntegerField()), 0) +
            Coalesce(Subquery(answer_rating, output_field=IntegerField()), 0)
        ).order_by('-week_rating')[:10]
