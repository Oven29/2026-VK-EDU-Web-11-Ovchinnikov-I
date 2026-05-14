from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .models import Question, Tag, Answer
from .utils import paginate
from .forms import QuestionForm, AnswerForm


def index(request):
    page_obj = paginate(Question.objects.new(), request)
    context = {
        'questions': page_obj,
    }

    return render(request, 'questions/index.html', context)


def question(request, pk: int):
    question_obj = get_object_or_404(
        Question.objects.select_related('author').prefetch_related('tags'),
        pk=pk,
    )
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(author=request.user, question=question_obj)
            # Redirect to the last page of answers or just back to the question
            return redirect(reverse('question', kwargs={'pk': pk}) + f'#answer-{answer.id}')
    else:
        form = AnswerForm()

    answers = question_obj.answers.all().select_related('author')
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
    page_obj = paginate(Question.objects.by_tag(tag_obj.name), request)
    context = {
        'questions': page_obj,
        'title': f'Tag: {tag_obj}',
    }

    return render(request, 'questions/index.html', context)


def hot(request):
    page_obj = paginate(Question.objects.hot(), request)
    context = {
        'questions': page_obj,
        'title': 'Hot Questions',
    }

    return render(request, 'questions/index.html', context)


def user_questions(request, username: str):
    user = get_object_or_404(User, username=username)
    page_obj = paginate(Question.objects.by_author(user.username), request)
    context = {
        'questions': page_obj,
        'title': f'{username}\'s questions',
    }

    return render(request, 'questions/index.html', context)
