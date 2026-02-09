from django.db import models

class AuditModel(models.Model):
    created_date = models.DateTimeField(auto_now_add = True, editable = False)
    modified_date = models.DateTimeField(auto_now_add = True, editable = False)
    version = models.PositiveIntegerField(default = 0)
    created_by = models.CharField(max_length = 50, default = "admin")
    modified_by = models.CharField(max_length = 50, default = "admin")
    
    class Meta:
        # This model will not create any database table
        abstract = True