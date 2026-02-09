# Python base imports - Default ones

# Dependent software imports
from rest_framework import serializers

# Custom created imports
from app1.models import Question, Choice, Answers


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "pub_date", "question_text"]


# if used HyperlinkedModelSerializer, then we need to send the POST call like this -

# {
#     "question": "http://127.0.0.1:8080/question/1/",
#     "choice_text": "New Delhi, Mumbai, Chennai, Kolkata",
#     "votes": 6
# }
# class ChoiceSerializer(serializers.HyperlinkedModelSerializer):

# If used ModelSerializer, then we need to send the POST call like this -

#{
#     "question": 1,
#     "choice_text": "New Delhi, Mumbai, Chennai, Kolkata",
#     "votes": 6
# }

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "question", "choice_text", "votes"]

class AnswersSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Answers
        fields = ["id", "answer", "created_by"]