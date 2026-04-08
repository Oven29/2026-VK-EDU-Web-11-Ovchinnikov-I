from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('question/<int:pk>/', views.question, name='question'),
    path('ask/', views.ask, name='ask'),
    path('tag/<str:tag>/', views.tag, name='tag'),
    path('hot/', views.hot, name='hot'),
]
