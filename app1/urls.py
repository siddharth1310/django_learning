# Python base imports - Default ones

# Dependent software imports
from django.urls import path
from rest_framework import routers

# Custom created imports
from app1.views import QuestionViewSet, ChoiceViewSet, AnswersViewSet, index

router = routers.DefaultRouter()
router.register(r"question", QuestionViewSet)
router.register(r"choice", ChoiceViewSet)
router.register(r"answers", AnswersViewSet)

urlpatterns = [
    path("", index, name = "index"),
]