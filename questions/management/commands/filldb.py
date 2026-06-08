import random
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db.models import Sum, OuterRef, Subquery
from django.db.models.functions import Coalesce
from faker import Faker

from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike
from core.models import Profile


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.faker = Faker()
        self.ratio = 0  # Initialize property

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Коэффициент заполнения')

    def _log(self, message):
        """Internal logging method."""
        self.stdout.write(message)

    def handle(self, *args, **kwargs):
        self.ratio = kwargs['ratio']

        if self.ratio > 100_000:
            raise CommandError(
                'Коэффициент заполнения не должен превышать 100000.')
        if self.ratio <= 0:
            raise CommandError('Коэффициент должен быть положительным числом.')

        # Process flow using private methods
        tags = self._create_tags()
        users = self._create_users()
        questions = self._create_questions(users, tags)
        self._create_answers(users, questions)
        self._create_likes(users, questions)
        self._recalculate_ratings()

        self._log("Готово!")

    def _create_tags(self):
        tags = [
            Tag(name=f'{self.faker.word()}_{random.randint(1, 1000000)}')
            for _ in range(self.ratio)
        ]
        Tag.objects.bulk_create(tags, batch_size=10000)
        self._log(f'Создано тегов: {len(tags)}')
        return list(Tag.objects.order_by('-id')[:self.ratio])

    def _create_users(self):
        users_to_create = []
        for _ in range(self.ratio):
            username = f"{self.faker.user_name()}_{random.randint(1, 1000000)}"
            users_to_create.append(User(
                username=username,
                first_name=self.faker.first_name(),
                last_name=self.faker.last_name(),
                email=self.faker.email(),
                password=make_password(self.faker.password()),
            ))
        User.objects.bulk_create(
            users_to_create, batch_size=10000, ignore_conflicts=True)

        all_users = list(User.objects.order_by('-id')[:self.ratio])

        profiles = [Profile(user=u) for u in all_users]
        Profile.objects.bulk_create(
            profiles, batch_size=10000, ignore_conflicts=True)

        self._log(f'Создано пользователей: {len(all_users)}')
        return all_users

    def _create_questions(self, users, tags):
        questions_to_create = []
        for _ in range(self.ratio * 10):
            questions_to_create.append(Question(
                title=self.faker.sentence()[:50],
                content=self.faker.text(),
                author=random.choice(users),
            ))
        Question.objects.bulk_create(questions_to_create, batch_size=10000)

        all_questions = list(
            Question.objects.order_by('-id')[:self.ratio * 10])
        self._log(f'Создано вопросов: {len(all_questions)}')

        QuestionTagRel = Question.tags.through
        relations = []
        for q in all_questions:
            chosen_tags = random.sample(tags, random.randint(2, 3))
            for t in chosen_tags:
                relations.append(QuestionTagRel(question_id=q.id, tag_id=t.id))

        QuestionTagRel.objects.bulk_create(relations, batch_size=10000)
        return all_questions

    def _create_answers(self, users, questions):
        answers_batch = []
        total_count = self.ratio * 100
        for _ in range(total_count):
            answers_batch.append(Answer(
                text=self.faker.paragraph(),
                author=random.choice(users),
                question=random.choice(questions),
                is_correct=random.choice([False] * 10 + [True])
            ))
            if len(answers_batch) >= 10000:
                Answer.objects.bulk_create(answers_batch, batch_size=10000)
                answers_batch = []

        if answers_batch:
            Answer.objects.bulk_create(answers_batch, batch_size=10000)

        self._log(f'Создано ответов: {total_count}')

    def _create_likes(self, users, questions):
        # Questions
        self._bulk_generate_likes(
            QuestionLike, questions, users, self.ratio * 100, 'question_id')

        # Answers
        all_answer_ids = list(Answer.objects.order_by(
            '-id')[:self.ratio * 100].values_list('id', flat=True))
        self._bulk_generate_likes(
            AnswerLike, all_answer_ids, users, self.ratio * 100, 'answer_id')

        self._log('Заполнение лайков завершено')

    def _bulk_generate_likes(self, model_class, targets, users, count, target_field):
        """Internal helper for likes generation."""
        likes = []
        already_exists = set()
        user_ids = [u.id for u in users]

        for _ in range(count):
            u_id = random.choice(user_ids)
            target = random.choice(targets)
            t_id = target.id if hasattr(target, 'id') else target

            if (u_id, t_id) not in already_exists:
                already_exists.add((u_id, t_id))
                likes.append(model_class(**{
                    'user_id': u_id,
                    target_field: t_id,
                    'value': random.choice([-1, 1, 1])
                }))

                if len(likes) >= 20000:
                    model_class.objects.bulk_create(
                        likes, batch_size=10000, ignore_conflicts=True)
                    likes = []

        if likes:
            model_class.objects.bulk_create(
                likes, batch_size=10000, ignore_conflicts=True)

    def _recalculate_ratings(self):
        self._log("Пересчитываю рейтинги вопросов...")
        q_sum = QuestionLike.objects.filter(
            question=OuterRef('pk')
        ).values('question').annotate(total=Sum('value')).values('total')
        Question.objects.update(rating=Coalesce(Subquery(q_sum), 0))

        self._log("Пересчитываю рейтинги ответов...")
        a_sum = AnswerLike.objects.filter(
            answer=OuterRef('pk')
        ).values('answer').annotate(total=Sum('value')).values('total')
        Answer.objects.update(rating=Coalesce(Subquery(a_sum), 0))

        self._log("Рассчитал рейтинг вопросов и ответов")
