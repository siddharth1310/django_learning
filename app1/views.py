# Python base imports - Default ones

# Dependent software imports
from rest_framework import viewsets
from django.http import HttpResponse

# Custom created imports
from app1.models import Question, Choice, Answers
from app1.serializers import QuestionSerializer, ChoiceSerializer, AnswersSerializer

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer


class AnswersViewSet(viewsets.ModelViewSet):
    queryset = Answers.objects.all()
    serializer_class = AnswersSerializer