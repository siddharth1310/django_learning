from rest_framework import serializers

from file_mgr.models import UploadFile


# serializers.py
class SimpleFileUploadSerializer(serializers.Serializer):  # ← Changed!
    file_object = serializers.FileField(required=True)

    def validate_file_object(self, value):
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("File too large")
        return value


class MultipleFileUploadSerializer(serializers.ListSerializer):
    child = SimpleFileUploadSerializer()


class UploadFileDetailSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UploadFile
        fields = [
            'id', 'file_name', 'original_file_name', 'mime_type', 
            'file_path', 'upload_path', 'extracted_files_info', 'file_metadata',
            'download_url', 'created_by'
        ]
        read_only_fields = fields  # All read-only for detail view

    def get_download_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.file_object.url) if obj.file_object else None
