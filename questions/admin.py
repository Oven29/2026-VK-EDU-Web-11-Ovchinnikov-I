from django.contrib import admin

from .models import Tag, Question, Answer, QuestionLike, AnswerLike


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    raw_id_fields = ('author',)
    fields = ('author', 'content', 'is_correct', 'rating', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'rating', 'created_at')
    list_select_related = ('author',)
    list_filter = ('created_at', 'tags')
    search_fields = ('title', 'content')
    raw_id_fields = ('author',)
    filter_horizontal = ('tags',)
    inlines = [AnswerInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'author', 'is_correct', 'rating', 'created_at')
    list_select_related = ('author', 'question')
    list_filter = ('is_correct', 'created_at')
    search_fields = ('content',)
    raw_id_fields = ('author', 'question')


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'value', 'created_at')
    list_select_related = ('user', 'question')
    list_filter = ('value',)
    raw_id_fields = ('user', 'question')


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'answer', 'value', 'created_at')
    list_select_related = ('user', 'answer')
    list_filter = ('value',)
    raw_id_fields = ('user', 'answer')
