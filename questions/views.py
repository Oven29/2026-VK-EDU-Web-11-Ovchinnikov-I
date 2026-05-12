from django.shortcuts import render, get_object_or_404

from .models import Question, Tag
from .utils import paginate


ME = {
    "name": "Ivan. O",
    "profile_path": "#",
    "profile_photo": "https://i.yapx.ru/dkv1w.jpg",
}


def index(request):
    page_obj = paginate(Question.objects.new(), request)
    context = {
        'me': ME,
        'questions': page_obj,
    }

    return render(request, 'questions/index.html', context)


def question(request, pk: int):
    question = get_object_or_404(
        Question.objects.select_related('author').prefetch_related('tags'),
        pk=pk,
    )
    answers = question.answers.all().select_related('author')
    page_obj = paginate(answers, request)
    context = {
        'me': ME,
        'question': question,
        'answers': page_obj,
    }

    return render(request, 'questions/question.html', context)


def ask(request):
    context = {
        'me': ME,
    }

    return render(request, 'questions/ask.html', context)


def tag(request, tag: str):
    tag = get_object_or_404(Tag, name=tag)
    page_obj = paginate(Question.objects.by_tag(tag.name), request)
    context = {
        'me': ME,
        'questions': page_obj,
        'tag': tag,
        'title': f'Tag: {tag}',
    }

    return render(request, 'questions/index.html', context)


def hot(request):
    page_obj = paginate(Question.objects.hot(), request)
    context = {
        'me': ME,
        'questions': page_obj,
        'hot': True,
        'title': 'Hot Questions',
    }

    return render(request, 'questions/index.html', context)
