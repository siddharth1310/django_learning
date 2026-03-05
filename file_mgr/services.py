from rest_framework.exceptions import ValidationError
from .models import UploadFile

class FileManager:
    @staticmethod
    def create_upload(data, user=None):
        """Create upload instance; save() populates fields."""
        if user:
            data['created_by'] = user  # For AuditModel
        if 'upload_path' in data:
            # Integrate upload_path into path if needed (customize upload_to)
            pass
        upload = UploadFile(**data)
        upload.save()
        return upload

    @staticmethod
    def update_upload(instance_id, data, user):
        """Update with new file/metadata."""
        try:
            instance = UploadFile.objects.get(id=instance_id, created_by=user)
        except UploadFile.DoesNotExist:
            raise ValidationError("File not found")
        for attr, value in data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    @staticmethod
    def delete_upload(instance_id, user):
        """Soft/hard delete with audit."""
        instance = UploadFile.objects.get(id=instance_id, created_by=user)
        if instance.file_object:
            instance.file_object.delete(save=False)
        instance.delete()
        return True
