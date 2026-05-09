from django.shortcuts import render


def index(request):
    return render(request, 'questions/index.html')


def question(request, pk: int):
    print(pk)
    return render(request, 'questions/question.html')


def ask(request):
    return render(request, 'questions/ask.html')


def tag(request, tag: str):
    return render(request, 'questions/tag.html')


def hot(request):
    return render(request, 'questions/hot.html')
