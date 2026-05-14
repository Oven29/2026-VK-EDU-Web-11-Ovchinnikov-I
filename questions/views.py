from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import F, Value, OuterRef, Subquery, IntegerField

from .models import Question, Tag, Answer, QuestionLike, AnswerLike
from .utils import paginate
from .forms import QuestionForm, AnswerForm


def index(request):
    page_obj = paginate(Question.objects.new(request.user), request)
    context = {
        'questions': page_obj,
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
            answer = form.save(author=request.user, question=question_obj)
            return redirect(reverse('question', kwargs={'pk': pk}) + f'#answer-{answer.id}')
    else:
        form = AnswerForm()

    answers_qs = question_obj.answers.all().select_related('author')

    if request.user.is_authenticated:
        vote_subquery = AnswerLike.objects.filter(
            user=request.user,
            answer=OuterRef('pk')
        ).values('value')
        answers_qs = answers_qs.annotate(user_vote=Subquery(vote_subquery))
    else:
        answers_qs = answers_qs.annotate(
            user_vote=Value(0, output_field=IntegerField()))

    answers = answers_qs.order_by('-is_correct', '-created_at')
    page_obj = paginate(answers, request)
    context = {
        'question': question_obj,
        'answers': page_obj,
        'form': form,
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
        'title': f'Tag: {tag_obj}',
    }

    return render(request, 'questions/index.html', context)


def hot(request):
    page_obj = paginate(Question.objects.hot(request.user), request)
    context = {
        'questions': page_obj,
        'title': 'Hot Questions',
    }

    return render(request, 'questions/index.html', context)


def user_questions(request, username: str):
    user = get_object_or_404(User, username=username)
    page_obj = paginate(Question.objects.by_author(
        user.username, request.user), request)
    context = {
        'questions': page_obj,
        'title': f'{username}\'s questions',
    }

    return render(request, 'questions/index.html', context)


@login_required
@require_POST
def vote_question(request):
    question_id = request.POST.get('id')
    vote_type = request.POST.get('type')  # 'up' or 'down'

    question_obj = get_object_or_404(Question, pk=question_id)
    value = 1 if vote_type == 'up' else -1

    like, created = QuestionLike.objects.get_or_create(
        user=request.user,
        question=question_obj,
        defaults={'value': value}
    )

    if not created:
        if like.value == value:
            # Re-click on same button = remove vote
            like.delete()
            question_obj.rating = F('rating') - value
        else:
            # Change vote
            like.value = value
            like.save()
            question_obj.rating = F('rating') + 2 * value
    else:
        question_obj.rating = F('rating') + value

    question_obj.save()
    question_obj.refresh_from_db()

    return JsonResponse({'rating': question_obj.rating})


@login_required
@require_POST
def vote_answer(request):
    answer_id = request.POST.get('id')
    vote_type = request.POST.get('type')

    answer_obj = get_object_or_404(Answer, pk=answer_id)
    value = 1 if vote_type == 'up' else -1

    like, created = AnswerLike.objects.get_or_create(
        user=request.user,
        answer=answer_obj,
        defaults={'value': value}
    )

    if not created:
        if like.value == value:
            like.delete()
            answer_obj.rating = F('rating') - value
        else:
            like.value = value
            like.save()
            answer_obj.rating = F('rating') + 2 * value
    else:
        answer_obj.rating = F('rating') + value

    answer_obj.save()
    answer_obj.refresh_from_db()

    return JsonResponse({'rating': answer_obj.rating})


@login_required
@require_POST
def mark_correct(request):
    answer_id = request.POST.get('id')
    answer_obj = get_object_or_404(Answer, pk=answer_id)

    if request.user != answer_obj.question.author:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    if answer_obj.is_correct:
        answer_obj.is_correct = False
        answer_obj.save()
    else:
        answer_obj.question.answers.all().update(is_correct=False)
        answer_obj.is_correct = True
        answer_obj.save()

    return JsonResponse({'success': True, 'is_correct': answer_obj.is_correct})
