# Python base imports - Default ones

# Dependent software imports
from django.db import models

# Custom created imports
from app2.models import AuditModel

class GlobalAppConfig(AuditModel):
    category = models.CharField(max_length = 32, null = False)
    name = models.CharField(max_length = 64, null = False, unique = True)
    value = models.CharField(max_length = 32, null = False)

    REQUIRED_FIELDS = ["category", "name", "value"]

    def __str__(self):
        return f"{self.__class__.__name__} - {str(self.name)}"
    
    class Meta(AuditModel.Meta):
        db_table = "global_app_config"
        indexes = [
            models.Index(fields = ["category"], name = "config-category-idx"), 
            models.Index(fields = ["name"], name = "config-name-idx"), 
        ]
