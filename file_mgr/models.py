# Python base imports - Default ones
from datetime import datetime

# Dependent software imports
from django.db import models
from django.db.models import JSONField
import os
# import zipfile
# from django.core.files.base import ContentFile
# from PIL import Image  # For image metadata example
# Custom created imports
from app2.models import AuditModel

def upload_to(instance, filename):
    created_by = instance.created_by.employee_id
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_name = f"{created_by}_{timestamp}_{filename}"
    return f"user_{created_by}/uploaded/{unique_name}"
    

class UploadFile(AuditModel):
    file_object = models.FileField(upload_to = upload_to, null = True, editable = False, blank = True)
    file_name = models.CharField(max_length = 255, null = False, blank = False, unique = False, help_text = "Name of the stored file (final name on disk).")
    original_file_name = models.CharField(max_length = 255, null = True, blank = True, help_text = "Original filename as uploaded by client")
    mime_type = models.CharField(max_length = 128, null = True, blank = True, help_text = "MIME type string, e.g, 'application/pdf'")
    file_path = models.CharField(max_length = 512, null = True, blank = True, help_text = "Relative path like 'user_123/filename.txt")
    upload_path = models.CharField(max_length = 128, null = True, blank = True, help_text = "Optional logical subfolder provided by the client.")
    extracted_files_info = JSONField(null = True, blank = True, help_text = "JSONB storing details of extracted files inside a ZIP archive.")
    file_metadata = JSONField(null = True, blank = True)

    def __str__(self) -> str:
        return self.file_name

    class Meta(AuditModel.Meta):
        db_table = "uploaded_files"
        ordering = ["id"]
        indexes = [models.Index(fields = ["file_name"], name = "idx_file_name")]

    def save(self, *args, **kwargs):
        # Paths only - no content_type handling
        if self.file_object and self.file_object.name:
            self.file_path = self.file_object.name
            self.file_name = os.path.basename(self.file_path)
        
        super().save(*args, **kwargs)




    # def _extract_zip_info(self):
    #     """Extract ZIP contents list."""
    #     if zipfile.is_zipfile(self.file_object.path):
    #         with zipfile.ZipFile(self.file_object.path, 'r') as zip_ref:
    #             return [{'name': f.filename, 'size': f.file_size} for f in zip_ref.infolist()]
    #     return None

    # def _get_metadata(self):
    #     """Example: Image dimensions."""
    #     try:
    #         with Image.open(self.file_object.path) as img:
    #             return {'width': img.width, 'height': img.height}
    #     except:
    #         return None