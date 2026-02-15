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
    SnippetViewSet,
    UserDetail,
    UserList,
    UserViewSet,
    api_root, 
    index, 
    # snippet_detail, 
    # snippet_list
    )

"""
DefaultRouter automatically generates URL patterns from ViewSets:
- Maps actions to HTTP methods and URL paths
- Creates URL names for reverse() lookups (user-list, snippet-detail, etc.)
- Handles basename for models without get_absolute_url()
- Provides root API view at / with links to all registered ViewSets
"""
router = routers.DefaultRouter()
router.register(r"question", QuestionViewSet)
router.register(r"choice", ChoiceViewSet)
router.register(r"answers", AnswersViewSet)

"""
Using Routers

Because we are using ViewSet classes rather View classes, we actually don't need to design the URL conf ourselves.
The conventions for wiring up resources into views and urls can be handled automatically, using a Router class. All
we need to do is register the appropriate view sets with a router, let it do the rest.
"""
router.register(r"users", UserViewSet, basename = "user")
router.register(r"snippets", SnippetViewSet, basename = "snippet")

urlpatterns = [
    # path("", index, name = "index"), 
    # path("", api_root), 
    
    # path("snippets/", snippet_list), 
    # path("snippets/<int:pk>/", snippet_detail), 
    
    # path("snippets/", SnippetList.as_view(), name = "snippet-list"),  
    # path("snippets/<int:pk>/", SnippetDetail.as_view(), name = "snippet-detail"), 
    # path("snippets/<int:pk>/highlight/", SnippetHighlight.as_view(), name = "snippet-highlight"), 
    
    
    # NOTE - below endpoints not required if you are using ViewSet classes
    # path("users/", UserList.as_view(), name = "user-list"), 
    # path("users/<int:pk>/", UserDetail.as_view(), name = "user-detail"), 
]