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
        'author': {
            'name': f'User_{i}',
            "profile_path": "#",
            "profile_photo": "https://i.yapx.ru/dkv1w.jpg",
        },
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
        'author': {
            'name': f'Ivan_{i}',
            "profile_path": "#",
            "profile_photo": "https://i.yapx.ru/dkv1w.jpg",
        },
        'created_at': f'2026-03-{(i % 30) + 1:02d}',
        'tags': [TAGS[i % len(TAGS)], TAGS[(i + 1) % len(TAGS)]],
        'rating': i * 3 - 10,
        'answers_count': i % 7,
    })

QUESTIONS[2]["tags"] = TAGS


BEST_MEMBERS = [
    {
        "name": "Ivan. O",
        "profile_path": "#",
    },
    {
        "name": "Gazan G.",
        "profile_path": "#67",
    },
    {
        "name": "Anton Chufashin",
        "profile_path": "#",
    }
]

ME = {
    "name": "Ivan. O",
    "profile_path": "#",
    "profile_photo": "https://i.yapx.ru/dkv1w.jpg",
}


def index(request):
    page_obj = paginate(QUESTIONS, request, per_page=10)
    context = {
        'me': ME,
        'questions': page_obj,
        'tags': TAGS[:10],
        'best_members': BEST_MEMBERS,
    }

    return render(request, 'questions/index.html', context)


def question(request, pk: int):
    question = next((q for q in QUESTIONS if q['id'] == pk), QUESTIONS[0])
    if question is None:
        # Заглушка
        return redirect('index')

    page_obj = paginate(ANSWERS, request, per_page=5)
    context = {
        'me': ME,
        'question': question,
        'answers': page_obj,
        'tags': TAGS[:10],
        'best_members': BEST_MEMBERS,
    }

    return render(request, 'questions/question.html', context)


def ask(request):
    context = {
        'me': ME,
        'best_members': BEST_MEMBERS,
    }

    return render(request, 'questions/ask.html', context)


def tag(request, tag: str):
    questions = [q for q in QUESTIONS if tag in q['tags']]
    page_obj = paginate(questions, request, per_page=10)
    context = {
        'me': ME,
        'questions': page_obj,
        'tag': tag,
        'tags': TAGS[:10],
        'title': f'Tag: {tag}',
        'best_members': BEST_MEMBERS,
    }

    return render(request, 'questions/index.html', context)


def hot(request):
    questions = sorted(QUESTIONS, key=lambda q: q['rating'], reverse=True)
    page_obj = paginate(questions, request, per_page=10)
    context = {
        'me': ME,
        'questions': page_obj,
        'tags': TAGS[:10],
        'hot': True,
        'title': 'Hot Questions',
        'best_members': BEST_MEMBERS,
    }

    return render(request, 'questions/index.html', context)
