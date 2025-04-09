from django.contrib import admin

# Register your models here.
# surveys/admin.py
from django.contrib import admin
from .models import Survey, Question, QuestionOption, Response, Answer

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    
class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]
    list_display = ('text', 'survey', 'question_type', 'required', 'order')
    list_filter = ('survey', 'question_type', 'required')
    search_fields = ('text', 'survey__title')

class SurveyAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('title', 'creator', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description', 'creator__username')
    date_hierarchy = 'created_at'

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'text_answer')

class ResponseAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ('survey', 'respondent_email', 'created_at')
    list_filter = ('survey', 'created_at')
    search_fields = ('survey__title', 'respondent_email')
    date_hierarchy = 'created_at'

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionOption)
admin.site.register(Response, ResponseAdmin)
admin.site.register(Answer)