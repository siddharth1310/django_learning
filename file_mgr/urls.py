# Python base imports - Default ones

# Dependent software imports
from rest_framework.routers import DefaultRouter

# Custom created imports
from file_mgr.views import UploadFileViewSet

router = DefaultRouter()
router.register(r"uploads", UploadFileViewSet, basename = "uploads")

urlpatterns = router.urls