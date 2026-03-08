# Python base imports - Default ones

# Dependent software imports
from rest_framework import serializers

# Custom created imports
from file_mgr.models import UploadFile


class UploadFileDetailSerializer(serializers.ModelSerializer):
    """
    DRF ModelSerializer for UploadFile model - used for API responses (list, retrieve, create).
    Converts model instances to JSON and handles validation for API endpoints.
    
    Key Features:
    - Serializes all essential UploadFile fields for API responses
    - Adds computed `download_url` field for direct file access
    - Handles both single file and multiple file responses uniformly
    """
    
    # Custom computed field - generates full download URL for uploaded files
    # SerializerMethodField() = read-only, computed per instance
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        """
        Serializer configuration - maps model fields to API response
        """
        model = UploadFile  # Source model for serialization
        
        # Fields included in JSON API response (exact order preserved)
        # Includes both model fields + computed download_url
        fields = ["id", "file_name", "mime_type", "file_path", "extracted_files_info", "file_metadata", 
            "download_url", "created_by", "file_object"]
    
    def get_download_url(self, obj):
        """
        Custom method to generate absolute download URL for uploaded files.
        
        <b>*Args*</b>
        - obj: UploadFile model instance
            
        <b>*Returns*</b>
        - str: Full absolute URL (e.g., "http://127.0.0.1:8000/media/user_123/file.pdf")
        - None: If no file or request context missing
        """
        # Get request object from serializer context (passed from ViewSet)
        request = self.context.get("request")
        
        # Safety checks - ensure both file exists and request is available
        if request and obj.file_object:
            # build_absolute_uri() converts relative media URL to full URL
            # obj.file_object.url = "/media/user_123/file.pdf"
            # → "http://127.0.0.1:8000/media/user_123/file.pdf"
            return request.build_absolute_uri(obj.file_object.url)
        
        # Fallback for missing file or request context
        return None
