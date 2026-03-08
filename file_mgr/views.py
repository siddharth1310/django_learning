# Python base imports - Default ones
from os import path

# Dependent software imports
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

# Custom created imports
from file_mgr.models import UploadFile
from file_mgr.serializers import UploadFileDetailSerializer

class UploadFileViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD API for UploadFile model with file upload support.
    
    Endpoints:
    - POST /api/uploads/          → Upload single/multiple files
    - GET  /api/uploads/          → List user's files  
    - GET  /api/uploads/{id}/     → Single file details
    - GET  /api/uploads/{id}/download/ → Download URL
    - DELETE /api/uploads/{id}/   → Delete file + storage cleanup
    
    Features:
    - Single parser handles both single & multiple file uploads
    - Unified response format (always "files" array)
    - Automatic file storage via upload_to
    - Proper cleanup on delete
    """

    # Global settings for ALL actions

    # All endpoints require authentication
    permission_classes = [IsAuthenticated]

    # Parse multipart/form-data uploads
    parser_classes = [MultiPartParser, FormParser]

    # Default serializer for all actions
    serializer_class = UploadFileDetailSerializer

    # Base queryset (filtered dynamically)
    queryset = UploadFile.objects.all()

    # Django-filter fields (if using django-filter)
    filterset_fields = ["created_by"]

    def get_serializer_context(self):
        """
        Ensure request context is passed to ALL serializers.
        Required for download_url generation in UploadFileDetailSerializer.
        """

        # Get parent context + add request object
        context = super().get_serializer_context()

        # Enables absolute URLs in serializer
        context["request"] = self.request
        return context


    def _handle_file_processing(self, file_object, request):
        """
        Process single uploaded file → create complete UploadFile record with correct paths.
        
        CRITICAL TIMING FIX: Ensures upload_to path generation happens BEFORE path extraction.
        
        Django FileField Flow (The Problem):
        1. file_object assignment → name = original filename
        2. save() → upload_to runs LATER 
        3. file_object.name updated AFTER save()
        
        This method forces upload_to to run IMMEDIATELY via file_object.save().
        
        Args:
            file_object: UploadedFile instance from request.FILES.getlist('file_object')
            request: DRF Request object (provides user context)
            
        Returns:
            dict: Complete serialized UploadFile data for API response
        """
        
        # STEP 1: Capture original metadata BEFORE Django modifies file_object
        # content_type gets lost after FileField assignment
        mime_type = file_object.content_type
        
        # STEP 2: Create model instance and assign file
        upload_file = UploadFile(created_by = request.user)
        upload_file.file_object = file_object  # FileField assignment (upload_to NOT run yet)
        
        # STEP 3: FORCE upload_to EXECUTION - CRITICAL FIX!
        # This line forces Django to:
        # - Run upload_to callable
        # - Generate final filename/path  
        # - Save physical file to disk
        # - Update file_object.name with correct relative path
        # 
        # Args breakdown:
        # - name: Current file_object.name (used by upload_to as base)
        # - file_object: Content to save
        # - save = False: DON'T trigger model save (prevents recursion)
        upload_file.file_object.save(
            upload_file.file_object.name,  # Current name (upload_to modifies this)
            file_object,                   # File content to save
            save = False                     # Prevent recursive model.save()
        )
        
        # STEP 4: NOW extract FINAL paths (upload_to has run!)
        # file_object.name is NOW the correct relative path from MEDIA_ROOT
        upload_file.mime_type = mime_type                          # Preserved original MIME type
        upload_file.file_path = upload_file.file_object.name       # ✅ "user_123/uploaded/123_..."
        upload_file.file_name = path.basename(upload_file.file_object.name)  # ✅ Just filename
        
        # STEP 5: Pure database save - no file operations
        # File already saved to disk, just persist metadata
        upload_file.save()
        
        # STEP 6: Serialize for API response with request context
        # Context enables absolute URLs in UploadFileDetailSerializer.download_url
        detail_serializer = UploadFileDetailSerializer(upload_file, context = {"request" : request})
        
        # Return dict (not Response) - caller wraps in Response()
        return detail_serializer.data


    def create(self, request, *args, **kwargs):
        """
        Handle file upload - SINGLE or MULTIPLE files.
        
        Request format (form-data):
        file_object=@file1.pdf
        file_object=@file2.pdf  (multiple = multiple rows with same key)
        
        Unified response format:
        ```
        {
          "message" : "2 file(s) uploaded successfully",
          "files" : [{...}, {...}]
        }
        ```
        """

        # Get all files with key 'file_object' (handles single/multiple)
        files = request.FILES.getlist("file_object")

        # Process each file identically
        results = []
        for file_obj in files:
            result_data = self._handle_file_processing(file_obj, request)
            results.append(result_data)
        
        # Always return array format - consistent for frontend
        return Response({"message" : f"{len(results)} file(s) uploaded successfully", "files" : results}, status = status.HTTP_201_CREATED)


    @action(detail = True, methods = ["get"])
    def download(self, request, pk = None):
        """
        Custom action: Get direct download URL for specific file.
        
        URL: /api/uploads/{id}/download/
        Method: GET
        
        <b>*Returns*</b>
        - "download_url" : "http://127.0.0.1:8080/media/user_123/file.pdf"
        """
        # Uses get_queryset() filtering
        instance = self.get_object()
        return Response({"download_url" : request.build_absolute_uri(instance.file_object.url)})


    def perform_destroy(self, instance):
        """
        Custom delete behavior - cleanup file storage.
        
        Override to delete physical file from disk before model deletion.
        Called automatically by DELETE /api/uploads/{id}/
        """

        # Delete physical file from MEDIA_ROOT
        if instance.file_object:
            # Don't trigger model save
            instance.file_object.delete(save = False)
        
        # Delete model record (AuditModel handles soft-delete if implemented)
        super().perform_destroy(instance)