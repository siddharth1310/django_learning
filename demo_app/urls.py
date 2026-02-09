"""
URL configuration for demo_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from oauth2_provider import urls as oauth2_urls
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from app1.urls import router as app1_router

# Routers provide a way of automatically determining the URL conf.
router = DefaultRouter()
router.registry.extend(app1_router.registry)

urlpatterns = [
    # Django Restframework routers
    path("", include(router.urls)),
    
    # This provides url endpoints - 
    # http://127.0.0.1:8080/api-auth/login/, http://127.0.0.1:8080/api-auth/login/logout/
    path("api-auth/", include("rest_framework.urls", namespace = "rest_framework")),
    
    # Default router provided by Django for Admin operations
    path("admin/", admin.site.urls),
    
    # OAuth routers
    path("o/", include(oauth2_urls)),
    
    # drf_spectacular routers
    path("api/schema/", SpectacularAPIView.as_view(), name = "schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name = "schema"), name = "swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name = "schema"), name = "redoc"),
    
    # Custom apps routers
    path("app1/", include("app1.urls")),
]
