# Python base imports - Default ones

# Dependent software imports
from django.urls import path
from rest_framework import routers

# Custom created imports
from app1.views import (
    QuestionViewSet, 
    ChoiceViewSet, 
    AnswersViewSet,
    SnippetDetail,
    SnippetHighlight,
    SnippetList,
    UserDetail,
    UserList,
    api_root, 
    index, 
    # snippet_detail, 
    # snippet_list
    )

router = routers.DefaultRouter()
router.register(r"question", QuestionViewSet)
router.register(r"choice", ChoiceViewSet)
router.register(r"answers", AnswersViewSet)

urlpatterns = [
    # path("", index, name = "index"), 
    path("", api_root), 
    
    # path("snippets/", snippet_list), 
    # path("snippets/<int:pk>/", snippet_detail), 
    
    path("snippets/", SnippetList.as_view(), name = "snippet-list"),  
    path("snippets/<int:pk>/", SnippetDetail.as_view(), name = "snippet-detail"), 
    path("snippets/<int:pk>/highlight/", SnippetHighlight.as_view(), name = "snippet-highlight"), 
    
    path("users/", UserList.as_view(), name = "user-list"), 
    path("users/<int:pk>/", UserDetail.as_view(), name = "user-detail"), 
]