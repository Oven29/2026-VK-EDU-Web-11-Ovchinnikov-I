from django.shortcuts import redirect, render
from .utils import paginate


TAGS = [
    'Python', 'Django', 'JavaScript', 'Docker', 'BMSTU', 
    'PostgreSQL', 'Go', 'React', 'Algorithms', 'WebRTC', 
    'CSS', 'HTML', 'Linux', 'SQLAlchemy', 'Git'
]

ANSWERS = [
    {
        'content': f'Answer body for question. This is a very helpful solution #{i}',
        'author': f'User_{i}',
        'created_at': '2026-04-08',
        'is_correct': i % 5 == 0,
        'rating': i * 2
    } for i in range(1, 10)
]

QUESTIONS = []

for i in range(1, 41):
    QUESTIONS.append({
        'id': i,
        'title': f'How to solve problem #{i}?',
        'content': f'Full description for question number {i}. I am having trouble with my implementation in the lab work. Any suggestions?',
        'author': f'Ivan_{i}',
        'created_at': f'2026-03-{ (i % 30) + 1:02d}',
        'tags': [TAGS[i % len(TAGS)], TAGS[(i + 1) % len(TAGS)]],
        'rating': i * 3 - 10,
        'answers_count': i % 7,
    })


def index(request):
    page_obj = paginate(QUESTIONS, request, per_page=10)
    context = {
        'questions': page_obj,
        'tags': TAGS[:10],
        'title': 'Ivan Ask'
    }

    return render(request, 'questions/index.html', context)


def question(request, pk: int):
    question = next((q for q in QUESTIONS if q['id'] == pk), QUESTIONS[0])
    if question is None:
        # Заглушка
        return redirect('index')

    page_obj = paginate(ANSWERS, request, per_page=5)
    context = {
        'question': question,
        'answers': page_obj,
        'tags': TAGS[:10],
    }
    
    return render(request, 'questions/question.html', context)


def ask(request):
    return render(request, 'questions/ask.html')


def tag(request, tag: str):
    questions = [q for q in QUESTIONS if tag in q['tags']]
    page_obj = paginate(questions, request, per_page=10)
    context = {
        'questions': page_obj,
        'tag': tag,
        'tags': TAGS[:10],
        'title': f'Tag: {tag}'
    }
    
    return render(request, 'questions/index.html', context)


def hot(request):
    questions = sorted(QUESTIONS, key=lambda q: q['rating'], reverse=True)
    page_obj = paginate(questions, request, per_page=10)
    context = {
        'questions': page_obj,
        'tags': TAGS[:10],
        'hot': True,
        'title': 'Hot Questions'
    }

    return render(request, 'questions/index.html', context)
