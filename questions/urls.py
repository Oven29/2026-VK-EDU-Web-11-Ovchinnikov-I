from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('question/<int:pk>/', views.question, name='question'),
    path('ask/', views.ask, name='ask'),
    path('tag/<str:tag>/', views.tag, name='tag'),
    path('hot/', views.hot, name='hot'),
    path('user/<str:username>/', views.user_questions, name='user_questions'),
    # AJAX
    path('vote/question/', views.vote_question, name='vote_question'),
    path('vote/answer/', views.vote_answer, name='vote_answer'),
    path('answer/correct/', views.mark_correct, name='mark_correct'),
]
