# Python base imports - Default ones

# Dependent software imports
from rest_framework import viewsets, status
from rest_framework.parsers import JSONParser
from django.http import HttpResponse, JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Custom created imports
from app1.models import Question, Choice, Answers, Snippet
from app1.serializers import QuestionSerializer, ChoiceSerializer, AnswersSerializer, SnippetSerializer

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@extend_schema(tags = ["app1 django starter"])
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().order_by("-created_date")
    serializer_class = QuestionSerializer
    
    # Protects the API as only when the user is authenticated, we allow them to access API.
    # If not verified, they will get below message - "detail: Authentication credentials were not provided."
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags = ["app1 django starter"])
class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all().order_by("-choice_text")
    serializer_class = ChoiceSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags = ["app1 django starter"])
class AnswersViewSet(viewsets.ModelViewSet):
    queryset = Answers.objects.all()
    serializer_class = AnswersSerializer
    permission_classes = [permissions.IsAuthenticated]


# NOTE - Because we want to be able to POST to this view from clients that won't have a CSRF token we need to mark
# the view as csrf_exempt. This isn't something that you would normally want to do, and REST framework views actually
# use more sensible behavior than this, but it will do for our purposes right now.

# OLD WAY - Refer to NEW WAY WRITTEN DOWN IN THE CODE SNIPPET
# @csrf_exempt
# def snippet_list(request) -> JsonResponse:
#     """
#     List all code snippets, or create a new project.
#     """
#     if request.method == "GET":
#         snippets = Snippet.objects.all()
#         serializer = SnippetSerializer(snippets, many = True)
#         return JsonResponse(serializer.data, safe = False)
#     elif request.method == "POST":
#         data = JSONParser().parse(request)
#         serializer = SnippetSerializer(data = data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data, status = status.HTTP_201_CREATED)
#         else:
#             return JsonResponse(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
#     else:
#         return JsonResponse({"detail" : "Method Not Allowed"}, status = status.HTTP_400_BAD_REQUEST)


# OLD WAY - Refer to NEW WAY WRITTEN DOWN IN THE CODE SNIPPET
# @csrf_exempt
# def snippet_detail(request, pk) -> HttpResponse | JsonResponse:
#     """
#     Retrieve, update or delete a code snippet
#     """
#     try:
#         snippet = Snippet.objects.get(pk = pk)
#     except Snippet.DoesNotExist:
#         return HttpResponse(status = status.HTTP_404_NOT_FOUND)
    
#     if request.method == "GET":
#         serializer = SnippetSerializer(snippet)
#         return JsonResponse(serializer.data)
#     elif request.method == "PUT":
#         data = JSONParser().parse(request)
#         serializer = SnippetSerializer(snippet, data = data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data)
#         else:
#             return JsonResponse(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
#     elif request.method == "DELETE":
#         snippet.delete()
#         return HttpResponse(status = status.HTTP_204_NO_CONTENT)
#     else:
#         return JsonResponse({"detail" : "Method Now Allowed"}, status = status.HTTP_400_BAD_REQUEST)


"""
Request objects
REST framework introduces a Request objet that extends the regular HttpRequest, and provides more flexible request parsing.
The core functionality of the Request object is the request.data attribute, which is similar to request.POST, but more useful
for working with Web APIs.
request.POST  # Only handles form data, Only works for 'POST' method
request.data  # Handles arbitrary data, Works for 'POST', 'PUT' and 'PATCH' methods


Response objects
REST framework also introduces a Response object, which is a type of TemplateResponse that takes unrendered content and uses
content negotiation to determine the correct content type to return to the client.
return Response(data)  # Renders to content type as requested by the client


Wrapping API views
REST framework provides two wrappers you can use to write API views. 
- The @api_view decorator for working with function-based views
- The APIView class for working with class-based views


NOTE - You may get below error -
AssertionError: Cannot apply DjangoModelPermissionOrAnonReadOnly on a view that does not set `.queryset` or have a `.get_queryset()`
method. 

Reason - `DjangoModelPermissionOrAnonReadOnly`set in settings.py 'REST_FRAMEWORK' section only works on views that are tied to a model
via .queryset or .get_queryset() [Typically GenericAPIView / ViewSets]. Below function 'snippet_list' is a function-based view (FBV), so
DRF can't figure out which model's permissions to check -> hence the AssertionError.

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES" : ["rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly",], 
    }

This permission class check Django's model permissions (add/change/delete/view) and needs to know which model applies to the view. DRF
determines that model from: view.queryset or view.get_queryset()

FBV don't have .queryset/.get_queryset(), so DRF raises:
AssertionError: Cannot apply DjangoModelPermissionOrAnonReadOnly on a view that does not set `.queryset` or have a `.get_queryset()`
method.


SOLUTION 1:
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def snippet_list(request):

SOLUTION 2:
Set this in settings.py
Old -> "DEFAULT_PERMISSION_CLASSES" : ["rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly",], 
New -> "DEFAULT_PERMISSION_CLASSES" : ["rest_framework.permissions.IsAuthenticated", ],
"""

@api_view(["GET", "POST"])
def snippet_list(request, format = None):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == "GET":
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many = True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = SnippetSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def snippet_detail(request, pk, format = None):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        snippet = Snippet.objects.get(pk = pk)
    except Snippet.DoesNotExist:
        return Response(status = status.HTTP_404_NOT_FOUND)
    
    if request.method == "GET":
        serializer = SnippetSerializer(snippet)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = SnippetSerializer(snippet, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        snippet.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)