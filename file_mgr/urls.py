from rest_framework.routers import DefaultRouter
from .views import UploadFileViewSet

router = DefaultRouter()
router.register(r"uploads", UploadFileViewSet, basename="uploads")  # Add basename!
urlpatterns = router.urls
