from django import forms
from django.db import transaction

from .models import Question, Answer, Tag


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        label='Теги',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'moon, park, puzzle'}),
        help_text='Введите теги через запятую.'
    )

    class Meta:
        model = Question
        fields = ('title', 'content', 'tags')
        labels = {
            'title': 'Заголовок',
            'content': 'Текст вопроса',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Как построить лунный парк?'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Опишите вашу проблему подробно...'}),
        }

    def _save_tags(self, question):
        tags_str = self.cleaned_data.get('tags', '')
        if tags_str:
            tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                question.tags.add(tag)

    def save(self, commit=True, author=None):
        question = super().save(commit=False)
        if author:
            question.author = author
        if commit:
            with transaction.atomic():
                question.save()
                self._save_tags(question)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('content',)
        labels = {
            'content': 'Ваш ответ',
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control mb-3',
                'rows': 5,
                'placeholder': 'Введите ваш ответ здесь...',
                'id': 'editor'
            }),
        }

    def save(self, commit=True, author=None, question=None):
        answer = super().save(commit=False)
        if author:
            answer.author = author
        if question:
            answer.question = question
        if commit:
            answer.save()
        return answer
