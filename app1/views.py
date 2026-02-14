# Python base imports - Default ones

# Dependent software imports
from rest_framework import viewsets, status
from rest_framework.parsers import JSONParser
from django.http import HttpResponse, JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from django.views.decorators.csrf import csrf_exempt

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
@csrf_exempt
def snippet_list(request) -> JsonResponse:
    """
    List all code snippets, or create a new project.
    """
    if request.method == "GET":
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many = True)
        return JsonResponse(serializer.data, safe = False)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = SnippetSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"detail" : "Method Not Allowed"}, status = status.HTTP_400_BAD_REQUEST)


# OLD WAY - Refer to NEW WAY WRITTEN DOWN IN THE CODE SNIPPET
@csrf_exempt
def snippet_detail(request, pk) -> HttpResponse | JsonResponse:
    """
    Retrieve, update or delete a code snippet
    """
    try:
        snippet = Snippet.objects.get(pk = pk)
    except Snippet.DoesNotExist:
        return HttpResponse(status = status.HTTP_404_NOT_FOUND)
    
    if request.method == "GET":
        serializer = SnippetSerializer(snippet)
        return JsonResponse(serializer.data)
    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = SnippetSerializer(snippet, data = data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        else:
            return JsonResponse(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        snippet.delete()
        return HttpResponse(status = status.HTTP_204_NO_CONTENT)
    else:
        return JsonResponse({"detail" : "Method Now Allowed"}, status = status.HTTP_400_BAD_REQUEST)