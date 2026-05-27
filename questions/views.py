from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.postgres.search import SearchVector, SearchQuery

from core.templatetags.core_tags import name_filter
from .models import Question, Tag, Answer, QuestionLike, AnswerLike
from .utils import paginate, get_centrifugo_token
from .forms import QuestionForm, AnswerForm
from .tasks import publish_answer_to_centrifugo, send_notification_email


def index(request):
    page_obj = paginate(Question.objects.new(request.user), request)
    context = {
        'questions': page_obj,
        'title': 'Новые вопросы',
    }

    return render(request, 'questions/index.html', context)


def question(request, pk: int):
    question_obj = get_object_or_404(
        Question.objects.with_user_vote(request.user).prefetch_related('tags'),
        pk=pk,
    )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = AnswerForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                answer = form.save(author=request.user, question=question_obj)
                request.user.profile.sync_answer_cnt()

            # Publish new answer notification to Centrifugo
            answer_data = {
                'id': answer.id,
                'content': answer.content,
                'author': {
                    'name': name_filter(answer.author),
                    'username': answer.author.username,
                    'profile_photo_url': answer.author.profile.photo.url if answer.author.profile.photo else None,
                },
                'created_at': answer.created_at.strftime('%H:%M:%S'),
            }
            publish_answer_to_centrifugo.delay(question_obj.id, answer_data)

            question_path = reverse('question', kwargs={'pk': pk}) +\
                f'#answer-{answer.id}'
            send_notification_email.delay(
                answer.author.email,
                request.build_absolute_uri(question_path),
                question_obj.title,
            )

            return redirect(question_path)
    else:
        form = AnswerForm()

    answers_qs = Answer.objects.get_for_question(question_obj, request.user)
    page_obj = paginate(answers_qs, request)

    # Generate connection token for Centrifugo
    user_id = str(request.user.id) if request.user.is_authenticated else ""
    centrifugo_token = get_centrifugo_token(user_id)

    context = {
        'question': question_obj,
        'answers': page_obj,
        'form': form,
        'centrifugo_token': centrifugo_token,
    }

    return render(request, 'questions/question.html', context)


@login_required
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question_obj = form.save(author=request.user)
            return redirect('question', pk=question_obj.pk)
    else:
        form = QuestionForm()

    return render(request, 'questions/ask.html', {'form': form})


def tag(request, tag: str):
    tag_obj = get_object_or_404(Tag, name=tag)
    page_obj = paginate(Question.objects.by_tag(
        tag_obj.name, request.user), request)
    context = {
        'questions': page_obj,
        'title': f'Тег: {tag_obj}',
    }

    return render(request, 'questions/index.html', context)


def hot(request):
    page_obj = paginate(Question.objects.hot(request.user), request)
    context = {
        'questions': page_obj,
        'title': 'Топовые вопросы',
    }

    return render(request, 'questions/index.html', context)


def user_questions(request, username: str):
    user = get_object_or_404(User, username=username)
    page_obj = paginate(Question.objects.by_author(
        user.id, request.user), request)
    context = {
        'questions': page_obj,
        'title': f'Вопросы пользователя {username}',
    }

    return render(request, 'questions/index.html', context)


@login_required
@require_POST
def vote_question(request, pk: int):
    vote_type = request.POST.get('type')
    value = 1 if vote_type == 'up' else -1

    question_obj = get_object_or_404(
        Question.objects.filter(is_active=True), pk=pk)
    rating = QuestionLike.objects.toggle_vote(
        request.user, question_obj, value)

    return JsonResponse({'rating': rating})


@login_required
@require_POST
def vote_answer(request, pk: int):
    vote_type = request.POST.get('type')
    value = 1 if vote_type == 'up' else -1

    answer_obj = get_object_or_404(
        Answer.objects.filter(is_active=True), pk=pk)
    rating = AnswerLike.objects.toggle_vote(request.user, answer_obj, value)

    return JsonResponse({'rating': rating})


@login_required
@require_POST
def mark_correct(request, pk: int):
    success, result = Answer.objects.toggle_correct(request.user, pk)

    if not success:
        return JsonResponse({'error': result}, status=403)

    return JsonResponse({'success': True, 'is_correct': result})


def search_api(request):
    """
    AJAX API for full-text search of questions.
    Returns top 5 relevant results as JSON.
    """
    query_text = request.GET.get('q', '')

    if len(query_text) < 3:
        return JsonResponse([], safe=False)

    # Perform full-text search across title and content
    vector = SearchVector('title', 'content')
    query = SearchQuery(query_text)

    results = Question.objects.annotate(
        search=vector
    ).filter(search=query).values('id', 'title')[:15]

    return JsonResponse(list(results), safe=False)
