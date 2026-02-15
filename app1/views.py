# Python base imports - Default ones

# Dependent software imports
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from drf_spectacular.utils import extend_schema
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, JsonResponse
from rest_framework import viewsets, status, mixins, generics, renderers
from rest_framework.decorators import api_view, action, permission_classes
from django_filters import UnknownFieldBehavior, rest_framework as filters

# Custom created imports
from app1.permissions import IsOwnerOrReadOnly
from app1.models import Question, Choice, Answers, Snippet
from app1.serializers import QuestionSerializer, ChoiceSerializer, AnswersSerializer, SnippetSerializer, UserSerializer

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

# @api_view(["GET", "POST"])
# def snippet_list(request, format = None):
#     """
#     List all code snippets, or create a new snippet.
#     """
#     if request.method == "GET":
#         snippets = Snippet.objects.all()
#         serializer = SnippetSerializer(snippets, many = True)
#         return Response(serializer.data)
#     elif request.method == "POST":
#         serializer = SnippetSerializer(data = request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status = status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


# @api_view(["GET", "PUT", "DELETE"])
# def snippet_detail(request, pk, format = None):
#     """
#     Retrieve, update or delete a code snippet.
#     """
#     try:
#         snippet = Snippet.objects.get(pk = pk)
#     except Snippet.DoesNotExist:
#         return Response(status = status.HTTP_404_NOT_FOUND)
    
#     if request.method == "GET":
#         serializer = SnippetSerializer(snippet)
#         return Response(serializer.data)
#     elif request.method == "PUT":
#         serializer = SnippetSerializer(snippet, data = request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
#     elif request.method == "DELETE":
#         snippet.delete()
#         return Response(status = status.HTTP_204_NO_CONTENT)


# ----------------------------------------- CLASS BASED VIEW IMPLEMENTATION -------------------------------- #

# ----------------------------------------- 1st way -------------------------------------------------------- #
# class SnippetList(APIView):
#     def get(self, request, format = None):
#         snippets = Snippet.objects.all()
#         serializer = SnippetSerializer(snippets, many = True)
#         return Response(serializer.data)
    
#     def post(self, request, format = None):
#         serializer = SnippetSerializer(data = request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status = status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


# class SnippetDetail(APIView):
#     def get_object(self, pk):
#         try:
#             return Snippet.objects.get(pk = pk)
#         except Snippet.DoesNotExist:
#             raise Http404
    
#     def get(self, request, pk, format = None):
#         snippet = self.get_object(pk)
#         serializer = SnippetSerializer(snippet)
#         return Response(serializer.data)
    
#     def put(self, request, pk, format = None):
#         snippet = self.get_object(pk)
#         serializer = SnippetSerializer(snippet, data = request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        
#     def delete(self, request, pk, format = None):
#         snippet = self.get_object(pk)
#         snippet.delete()
#         return Response(status = status.HTTP_204_NO_CONTENT)
# ----------------------------------------- 1st way -------------------------------------------------------- #


# ----------------------------------------- 2nd way -------------------------------------------------------- #
# class SnippetList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
    
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
    
#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)


# class SnippetDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
    
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
    
#     def put(self,request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)
    
#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)
# ----------------------------------------- 2nd way -------------------------------------------------------- #


# ----------------------------------------- 3rd way -------------------------------------------------------- #
class SnippetList(generics.ListCreateAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    
    # Only allow API access when the user is authenticated
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    # Only when the user is authenticated but still can read the data
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    # permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    
    """
    Associating Snippets with Users
    Right now, if we create a code snippet, there would be no way of associating the user that 
    created the snippet, with the snippet instance. The user isn't sent as part of the serialized
    representation, but is instead a property of the incoming request.
    The way we deal with that is by overriding a .perform_create() method on our snippet views,
    that allows us to modify how the instance save is managed, and handle any information that is 
    implicit in the incoming request or requested URL.
    """
    def perform_create(self, serializer):
        serializer.save(owner = self.request.user)


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    
    # Only allow API access when the user is authenticated
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
# ----------------------------------------- 3rd way -------------------------------------------------------- #


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(["GET"])
def api_root(request, format = None):
    """
    Root API endpoint providing hypermedia links to primary resources.
    Discovered-style API entry point that tells clients what resources are available.
    
    Uses reverse() with request=request to generate fully-qualified URLs including:
    - Current domain/protocol (http://localhost:8000)
    - Format suffix if requested (?format=json)
    - Proper URL names from urlconf
    
    Example response:
    {
        "users": "http://localhost:8000/users/",
        "snippets": "http://localhost:8000/snippets/"
    }
    """
    
    return Response(
        {
            "users" : reverse("user-list", request = request, format = format), 
            "snippets" : reverse("snippet-list", request = request, format = format), 
        }
    )


"""
Creating an endpoint for the highlighted snippets
Unlike all our other API endpoints, we don't want to use JSON, but instead just present an HTML representation.
There are two styles of HTML renderer provided by REST framework, one for dealing with HTML rendered using templates,
the other for dealing with pre-rendered HTML. The second renderer is the one we would like to use for this endpoint.

The other thing we need to consider when creating the code highlight view is that there's no existing concrete generic
view that we can use. We are not returning an object instance, but instead a property of an object instance.

Instead of using a concrete generic view, we will use the base class for representing instances, and create our own
.get() method.
"""
class SnippetHighlight(generics.GenericAPIView):
    """
    Custom view for syntax-highlighted HTML representation of snippets.
    
    Key differences from JSON APIs:
    1. Uses StaticHTMLRenderer instead of JSONRenderer - returns raw HTML
    2. No serializer_class needed - returns snippet.highlighted (pre-rendered HTML)
    3. No concrete generic view exists for property-based responses
    
    Access: /snippets/{id}/highlight/
    Response: Raw HTML of syntax-highlighted code (Content-Type: text/html)
    Browsable API: Shows rendered HTML directly in browser
    """
    
    queryset = Snippet.objects.all()
    renderer_classes = [renderers.StaticHTMLRenderer]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get(self, request, *args, **kwargs):
        """
        Custom .get() returns the pre-rendered highlighted HTML from snippet instance.
        get_object() provides standard lookup + permission checks.
        No serialization needed - highlighted field is already HTML-ready.
        """
        snippet = self.get_object()
        return Response(snippet.highlighted)


# ------------------------------ FILTERS IN DRF ----------------------------------------- #

# Custom filter method which can be defined out of the class scope.
# def filter_not_empty(queryset, name, value):
#     lookup = "__".join([name, "isnull"])
#     return queryset.filter(**{lookup : False})

"""
class SnippetFilter(filters.FilterSet):
    class Meta:
        model = Snippet
        fields = ["language", "style"]

IS EQUIVALENT TO

class SnippetViewSet(viewsets.ModelViewSet):
    # ----------- OTHER DEFINITIONS ----------- #
    filterset_fields = ("language", "style")
"""


class SnippetFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name = "price", lookup_expr = "gte")
    max_price = filters.NumberFilter(field_name = "price", lookup_expr = "lte")
    line_nos = filters.BooleanFilter(field_name = "linenos", label = "Is LineNos", lookup_expr = "exact")
    
    """  Filter for Books by if books are published or not  """
    # published = filters.BooleanFilter(field_name = "published_on", method = filter_not_empty)
    
    """  Filter for Books by if books are published or not  """
    # published = filters.BooleanFilter(field_name = "published_on", method = 'filter_not_empty')
    
    # def filter_not_empty(self, queryset, name, value):
    #     # Construct the full lookup expression.
    #     lookup = "__".join([name, "isnull"])
    #     return queryset.filter(**{lookup : False})

    #     # alternatively you could opt to hardcode the lookup. e.g,
    #     # return queryset.filter(published_on__isnull = False)
    
    
    class Meta:
        model = Snippet
        
        # Exclude one field for rest of the other to be used for filtration
        # exclude = ["style"]
        
        # fields = ["title", "language"]
        
        fields = {
            "title" : ["exact", "contains"], 
            "language" : ["exact", "contains"],
        }
        
        unknown_field_behavior = UnknownFieldBehavior.WARN


# ------------------------------------- TUTORIAL 6: Viewsets & Routers ----------------------------------------- #
"""
ViewSet classes are almost the same thing as view classes, except that they provide operations such as retrieve, 
or update, and not method handlers such as get or put.
A ViewSet class is only bound to a set of method handlers at the last moment, when it is instantiated into a set
of views, typically by using a Router class which handles the complexities of defining the URL conf for you.
"""

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnlyModelViewSet provides `list` and `retrieve` actions automatically.
    Perfect for User endpoints where we only need read access (no create/update/delete).
    
    Router generates:
    GET /users/          → list
    GET /users/{pk}/     → retrieve
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


"""
This time we have used the ModelViewSet class in order to get the complete set of default read and write operations.
Notice that we have also used the @action decorator to create a custom action, named highlight. This decorator can be 
used to add any custom endpoints that don't fit into the standard create/update/delete style.

Custom actions which use the @action decorator will respond to GET request by default. We can use the methods arguments
if we wanted an action that respond to POST requests.

The URLs for custom actions by default depend on the method name itself. If you want to change the way url should be 
constructed, you can include url_path as a decorator keyword argument.
"""
class SnippetViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet provides full CRUD: list, create, retrieve, update, destroy actions.
    Router generates standard RESTful URLs automatically:
    - GET    /snippets/          → list
    - POST   /snippets/          → create  
    - GET    /snippets/{pk}/     → retrieve
    - PUT    /snippets/{pk}/     → update
    - DELETE /snippets/{pk}/     → destroy
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    # Filter section
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_class = SnippetFilter
    
    def perform_create(self, serializer):
        """
        Automatically associates newly created snippets with the authenticated user.
        Called by create() action during serializer.save().
        """
        serializer.save(owner = self.request.user)
    
    @action(detail = True, renderer_classes = [renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        """
        Custom @action decorator creates new endpoint: /snippets/{pk}/highlight/
        detail=True → requires snippet pk (runs get_object())
        Returns highlighted HTML instead of JSON (StaticHTMLRenderer)
        Router auto-generates URL name: "snippet-highlight"
        """
        snippet = self.get_object()
        return Response(snippet.highlighted)


@permission_classes([permissions.IsAuthenticated])
class CreateRequestFromJSON(APIView):
    def post (self, request, format = None):
        try:
            input_request = request.data
            return Response(input_request, status = status.HTTP_200_OK)
        except Exception:
            return Response(status = status.HTTP_400_BAD_REQUEST)