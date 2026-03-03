# Python base imports - Default ones

# Dependent software imports
from django.urls import path

# Custom created imports
from app2.views import LoginAPIView

urlpatterns = [
    path("api/v1/auth/login/", LoginAPIView.as_view(), name = "login"),
]