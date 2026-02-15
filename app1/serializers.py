# Python base imports - Default ones

# Dependent software imports
from rest_framework import serializers
from django.contrib.auth.models import User

# Custom created imports
from app1.models import LANGUAGE_CHOICES, STYLE_CHOICES, Question, Choice, Answers, Snippet


class SnippetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only = True)
    title = serializers.CharField(required = False, allow_blank = True, max_length = 100)
    
    # The field flags can also control how the serializer should be displayed in certain circumstances, such as 
    # when rendering to HTML. The {'base_template' : 'textarea.html'} flag above is equivalent to using widget = widgets.
    # Textarea of a Django Form class. This is particularly useful for controlling how the browsable API should be displayed.
    code = serializers.CharField(style = {"base_template" : "textarea.html"})
    
    linenos = serializers.BooleanField(required = False)
    language = serializers.ChoiceField(choices = LANGUAGE_CHOICES, default = "python")
    style = serializers.ChoiceField(choices = STYLE_CHOICES, default = "friendly")
    highlighted = serializers.CharField(read_only = True, max_length = 1000)
    email = serializers.EmailField()
    results = serializers.CharField(max_length = 1000)
    price = serializers.IntegerField()
    
    # To handle foreign key - specify the related model/queryset
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(),  # Replace User with your actual model
        # write_only = True  # Use write_only if you don't want to expose it on GET
    )
    
    # The create() and update() methods define how fully fledged instances are created or modified when calling serializer.save()
    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        # Extract User instance and get its ID
        owner = validated_data.pop("owner_id")  # Gets <User: Wolverine1310>
        return Snippet.objects.create(
            owner_id = owner.id,  # Pass 100 (integer)
            **validated_data)
    
    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        
        instance.code = validated_data.get("code", instance.code)
        instance.style = validated_data.get("style", instance.style)
        instance.title = validated_data.get("title", instance.title)
        instance.linenos = validated_data.get("linenos", instance.linenos)
        instance.language = validated_data.get("language", instance.language)
        instance.style = validated_data.get("style", instance.style)
        instance.highlighted = validated_data.get("highlighted", instance.highlighted)
        instance.email = validated_data.get("email", instance.email)
        instance.results = validated_data.get("results", instance.results)
        instance.price = validated_data.get("price", instance.price)
        
        instance.save()
        return instance


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