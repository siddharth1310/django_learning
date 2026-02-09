# Python base imports - Default ones

# Dependent software imports
from django.db import models
from django.core.validators import MinLengthValidator

# Custom created imports
from app2.models import AuditModel

class Question(AuditModel):
    question_text = models.CharField(max_length = 200)
    pub_date = models.DateTimeField("date published")


class Choice(AuditModel):
    question = models.ForeignKey(Question, on_delete = models.CASCADE, related_name = "Choice_records")
    choice_text = models.CharField(max_length = 200)
    votes = models.IntegerField(default = 0)


class Answers(AuditModel):
    choice = models.ForeignKey(Choice, on_delete = models.CASCADE, related_name = "answer_records")
    answer = models.TextField(max_length = 4096, validators = [MinLengthValidator(3)], null = True, blank = True)