# Python base imports - Default ones

# Dependent software imports
from django.contrib import admin

# Custom created imports
from file_mgr.models import UploadFile


@admin.register(UploadFile)
class UploadFileAdmin(admin.ModelAdmin):
    """
    Custom Django Admin configuration for UploadFile model.
    Controls how the model appears and behaves in /admin/ interface.
    """
    
    # What columns to show in list view
    # Defines which model fields appear as columns in the admin list view table
    # Order matters - left to right display order
    list_display = ["file_name", "mime_type", "created_by"]
    
    # Filters in sidebar
    # Creates filter dropdowns in the right sidebar of list view
    # Users can click to filter records by these field values
    # Supports ForeignKey, CharField, DateField automatically
    list_filter = ["created_by", "mime_type"]
    
    # Search fields
    # Enables search box at top of list view
    # Django automatically creates SQL LIKE queries on these fields
    # Use __icontains for case-insensitive search, __exact for exact match
    search_fields = ["file_name", "mime_type"]
    
    # Order by newest first
    # Sets default sorting for list view (descending order with '-')
    # '-created_date' = newest first, 'created_date' = oldest first
    # Can be multiple fields: ['-created_date', 'file_name']
    ordering = ["-created_date"]
    
    # Items per page
    # Controls pagination - number of records shown per page in list view
    # Default is 100, common values: 10, 25, 50, 100
    list_per_page = 25
