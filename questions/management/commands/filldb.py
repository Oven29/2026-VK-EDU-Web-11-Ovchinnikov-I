import random
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.models import Sum, OuterRef, Subquery
from django.db.models.functions import Coalesce
from faker import Faker

from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike
from core.models import Profile


faker = Faker()


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Коэффициент заполнения')

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']

        if ratio > 100_000:
            raise CommandError(
                'Коэффициент заполнения не должен превышать 100000.')

        if ratio <= 0:
            raise CommandError('Коэффициент должен быть положительным числом.')

        # 1. Создаем теги
        tags = [Tag(name=f'{faker.word()}_{random.randint(1, 1000000)}')
                for _ in range(ratio)]
        Tag.objects.bulk_create(tags, batch_size=10000)
        self.stdout.write(f'Создано тегов: {len(tags)}')

        # 2. Создаем пользователей
        users = []
        for _ in range(ratio):
            username = f"{faker.user_name()}_{random.randint(1, 1000000)}"
            users.append(User(
                username=username,
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=faker.email(),
                password=faker.password(),
            ))
        User.objects.bulk_create(
            users, batch_size=10000, ignore_conflicts=True)

        # Подтягиваем созданных юзеров из базы (нужны ID)
        all_users = list(User.objects.order_by('-id')[:ratio])
        all_tags = list(Tag.objects.order_by('-id')[:ratio])

        # Создаем профили для новых юзеров (если они создаются автоматически через сигналы, этот шаг пропустить)
        profiles = [Profile(user=u) for u in all_users]
        Profile.objects.bulk_create(
            profiles, batch_size=10000, ignore_conflicts=True)
        self.stdout.write(f'Создано пользователей: {len(all_users)}')

        # 3. Создаем вопросы
        questions = []
        for _ in range(ratio * 10):
            questions.append(Question(
                title=faker.sentence()[:50],
                content=faker.text(),
                author=random.choice(all_users),
            ))
        Question.objects.bulk_create(questions, batch_size=10000)
        all_questions = list(Question.objects.order_by('-id')[:ratio * 10])
        self.stdout.write(f'Создано вопросов: {len(all_questions)}')

        # Привязываем теги (ManyToMany через промежуточную таблицу)
        QuestionTagRel = Question.tags.through
        relations = []
        for q in all_questions:
            # Рандомно 2-3 тега на вопрос
            chosen_tags = random.sample(all_tags, random.randint(2, 3))
            for t in chosen_tags:
                relations.append(QuestionTagRel(question_id=q.id, tag_id=t.id))

        # Используем пакетную вставку для связей тегов
        QuestionTagRel.objects.bulk_create(relations, batch_size=10000)

        # 4. Создаем ответы
        answers_batch = []
        for _ in range(ratio * 100):
            answers_batch.append(Answer(
                text=faker.paragraph(),
                author=random.choice(all_users),
                question=random.choice(all_questions),
                is_correct=random.choice([False] * 10 + [True])
            ))
            if len(answers_batch) >= 10000:
                Answer.objects.bulk_create(answers_batch, batch_size=10000)
                answers_batch = []
        Answer.objects.bulk_create(answers_batch, batch_size=10000)
        all_answer_ids = list(Answer.objects.order_by('-id')[:ratio * 100].values_list('id', flat=True))
        self.stdout.write(f'Создано ответов: {len(all_answer_ids)}')

        # 5. Создаем лайки (QuestionLike)
        question_likes = []
        already_exists = set()
        for _ in range(ratio * 100):
            user_id = random.choice(all_users).id
            question_id = random.choice(all_questions).id
            if not (user_id, question_id) in already_exists:
                already_exists.add((user_id, question_id))
                question_likes.append(QuestionLike(
                    user_id=user_id,
                    question_id=question_id,
                    value=random.choice([-1, 1, 1])
                ))
                if len(question_likes) >= 20000:
                    QuestionLike.objects.bulk_create(
                        question_likes,
                        batch_size=10000,
                        ignore_conflicts=True,
                    )
                    question_likes = []
        QuestionLike.objects.bulk_create(
            question_likes,
            batch_size=10000,
            ignore_conflicts=True,
        )

        # 6. Создаем лайки (AnswerLike)
        answer_likes = []
        already_exists = set()
        for _ in range(ratio * 100):
            answer_id = random.choice(all_answer_ids)
            user_id = random.choice(all_users).id
            if not (user_id, answer_id) in already_exists:
                already_exists.add((user_id, answer_id))
                answer_likes.append(AnswerLike(
                    user_id=user_id,
                    answer_id=answer_id,
                    value=random.choice([-1, 1, 1])
                ))
                if len(answer_likes) >= 20000:
                    AnswerLike.objects.bulk_create(
                        answer_likes,
                        ignore_conflicts=True,
                        batch_size=10000,
                    )
                    answer_likes = []
        AnswerLike.objects.bulk_create(
            answer_likes,
            ignore_conflicts=True,
            batch_size=10000,
        )

        self.stdout.write('Заполнение лайков завершено')

        # 7. Перерасчет рейтинга

        # Подзапрос для суммы лайков вопроса
        question_likes_sum = QuestionLike.objects.filter(
            question=OuterRef('pk')
        ).values('question').annotate(total=Sum('value')).values('total')

        # Обновляем все вопросы разом
        Question.objects.update(
            rating=Coalesce(Subquery(question_likes_sum), 0)
        )

        self.stdout.write("Пересчитываю рейтинги ответов...")

        # Аналогично для ответов
        answer_likes_sum = AnswerLike.objects.filter(
            answer=OuterRef('pk')
        ).values('answer').annotate(total=Sum('value')).values('total')

        Answer.objects.update(
            rating=Coalesce(Subquery(answer_likes_sum), 0)
        )

        self.stdout.write("Рассчитал рейтинг вопросов и ответов")

        self.stdout.write("Готово!")
