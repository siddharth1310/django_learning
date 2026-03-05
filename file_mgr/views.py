from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UploadFile
from .serializers import SimpleFileUploadSerializer, UploadFileDetailSerializer, MultipleFileUploadSerializer
import os

class UploadFileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == "create":
            return SimpleFileUploadSerializer
        return UploadFileDetailSerializer

    def get_queryset(self):
        return UploadFile.objects.filter(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        # Check if multiple files sent (key exists as list)
        files = request.FILES.getlist('file_object')
        
        if len(files) == 1:
            # Single file - use existing serializer logic
            return self._handle_single_file(files[0], request)
        else:
            # Multiple files - process each individually
            results = []
            for file_obj in files:
                result = self._handle_single_file(file_obj, request)
                results.append(result)
            
            return Response({
                'message': f'{len(results)} files uploaded successfully',
                'files': results
            }, status=status.HTTP_201_CREATED)

    def _handle_single_file(self, file_object, request):
        """Process single file (your existing logic)"""
        # Capture file info BEFORE assignment
        original_name = os.path.basename(file_object.name)
        mime_type = file_object.content_type
        
        # Create instance
        upload_file = UploadFile(created_by=request.user)
        upload_file.file_object = file_object
        upload_file.mime_type = mime_type  # Removed original_file_name per your request
        upload_file.save()
        
        # Serialize for response
        detail_serializer = UploadFileDetailSerializer(upload_file, context={'request': request})
        return detail_serializer.data



    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        instance = self.get_object()
        return Response(
            {"download_url": request.build_absolute_uri(instance.file_object.url)}
        )

    def perform_destroy(self, instance):
        if instance.file_object:
            instance.file_object.delete(save=False)
        super().perform_destroy(instance)
