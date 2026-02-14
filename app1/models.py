# Python base imports - Default ones

# Dependent software imports
from django.db import models
from pygments import highlight
from auditlog.registry import auditlog
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from auditlog.models import AuditlogHistoryField
from pygments.formatters.html import HtmlFormatter
from django.core.validators import MinLengthValidator
from encrypted_model_fields.fields import EncryptedCharField, EncryptedEmailField

# Custom created imports
from app2.models import AuditModel

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])


class Snippet(AuditModel):
    title = models.CharField(max_length = 100, blank = True, default = "")
    code = models.TextField()
    linenos = models.BooleanField(default = False)
    language = models.CharField(choices = LANGUAGE_CHOICES, default = "python", max_length = 100)
    style = models.CharField(choices = STYLE_CHOICES, default = "friendly", max_length = 100)
    
    owner = models.ForeignKey("auth.user", related_name = "snippets", on_delete = models.CASCADE)
    highlighted = models.TextField(default = "")
    email = EncryptedEmailField(default = "django_starter@gmail.com")
    results = EncryptedCharField(max_length = 60, default = "N/A")
    price = models.PositiveIntegerField(default = 0)
    
    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML representation
        of the code snippet.
        """
        
        lexer = get_lexer_by_name(self.language)
        linenos = "table" if self.linenos else False
        options = {"title" : self.title} if self.title else {}
        formatter = HtmlFormatter(style = self.style, linenos = linenos, full = True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        super().save(*args, **kwargs)
    
    class Meta(AuditModel.Meta):
        ordering = ["created_date"]


class Question(AuditModel):
    question_text = models.CharField(max_length = 200)
    pub_date = models.DateTimeField("date published")
    history = AuditlogHistoryField()
    
    class Meta(AuditModel.Meta):
        ordering = ["id"]


class Choice(AuditModel):
    question = models.ForeignKey(Question, on_delete = models.CASCADE, related_name = "Choice_records")
    choice_text = models.CharField(max_length = 200)
    votes = models.IntegerField(default = 0)
    
    class Meta(AuditModel.Meta):
        ordering = ["id"]


class Answers(AuditModel):
    choice = models.ForeignKey(Choice, on_delete = models.CASCADE, related_name = "answer_records")
    answer = models.TextField(max_length = 4096, validators = [MinLengthValidator(3)], null = True, blank = True)
    
    class Meta(AuditModel.Meta):
        # Specify the default ordering of the records when queried from the database.
        
        # ---------------------------------------------- EXPLANATION -------------------------------------------------
        # Since we are also using REST_FRAMEWORK's settings -
        #   "DEFAULT_PAGINATION_CLASS" : "rest_framework.pagination.PageNumberPagination", 
        #   "PAGE_SIZE" : 10,

        # Else we will get below warning -
        # UnorderedObjectListWarning: Pagination may yield inconsistent results with an unordered object_list:
        # <class 'app1.models.Question'> QuerySet.
        # paginator = self.django_paginator_class(queryset, pagesize)
        
        # This warning is issued by Django's paginator when you try to paginate a queryset that does not have a 
        # defined ordering. By default, if your Django model does not have a Meta ordering attribute defined and
        # you query the database without specifying an order, the queryset is unordered. When paginating unordered
        # querysets, the results can be inconsistent between pages because the database does not guarantee the order
        # of the returned rows.
        # -------------------------------------------------------------------------------------------------------------
        ordering = ["id"]


def custom_mask(value : str) -> str:
    return "****" + value[-4 : ]


# auditlog.register(Snippet)
# auditlog.register(Question, 
#                   mapping_fields = {"question_text" : "Question", "version" : "Question Version", }, 
#                   mask_fields = ["question_text"], 
#                   mask_callable = "app1.models.custom_mask")
# auditlog.register(Choice, exclude_fields = ["created_by"])
# auditlog.register(Answers)