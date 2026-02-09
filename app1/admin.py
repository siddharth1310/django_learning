# Python base imports - Default ones

# Dependent software imports
from django.contrib import admin

# Custom created imports
from app1.models import Question, Choice, Answers

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["id", "question_text"]
    search_fields = ["id", "question_text"]
    list_filter = ["id"]

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ["id", "choice_text"]
    search_fields = ["id", "choice_text"]
    list_filter = ["id"]

@admin.register(Answers)
class AnswersAdmin(admin.ModelAdmin):
    list_display = ["id", "answer"]
    search_fields = ["id", "answer"]
    list_filter = ["id"]