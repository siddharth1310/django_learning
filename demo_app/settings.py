from pathlib import Path
from os import environ, path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL = "/uploaded/"
MEDIA_ROOT = path.join("\\\\", BASE_DIR, "uploaded")

# GET Project Absolute Path
SITE_ROOT = path.dirname(path.dirname(path.realpath(__file__)))

STATIC_URL = "/static/"

# Where Django should look for "source" static files during development
STATICFILES_DIRS = [BASE_DIR / "static", ]

# Where collectstatic will put files for production serving
STATIC_ROOT = BASE_DIR / "staticfiles"

# ========================================================== SECURITY SECTION ==================================================================

SECRET_KEY = environ.get("APPDJANGO_KEY", "")

"""
There is a Django management command generate_encryption_key provided with the encrypted_model_fields library.
Use this command to generate a new encryption key to set as settings.FIELD_ENCRYPTION_KEY:
./manage.py generate_encryption_key
Running this command will print an encryption key to the terminal, which can be configured in your environment or settings file.

NOTE : This command will ONLY work in a CLEAN, NEW django project that does NOT import encrypted_model_fields in any of it's apps.
IF you are already importing encrypted_model_fields, try running this in a python shell instead:
import os
import base64
new_key = base64.urlsafe_b64encode(os.urandom(32))
print(new_key)
"""
FIELD_ENCRYPTION_KEY = environ.get("FIELD_ENCRYPTION_KEY", "")

SESSION_EXPIRE_AGE = environ.get("FIELD_ENCRYPTION_KEY", "")  # 20 min expiry since last activity
MAX_USER_SESSIONS = 3  # Allow only 3 concurrent user locations

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Specify allowed hosts (your Wildfly server's IP domain)
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "your_wildfly_ip_or_domain"]

# The list of extra HTTP headers to expose to the browser, in addition to the default safelisted headers.
# If non-empty, these are declared in the access-control-expose-headers header. Defaults to [].
CORS_EXPOSE_HEADERS = ["Content-Type", "X-CSRFToken"]

# If True, cookies will be allowed to be included in cross-site HTTP requests
CORS_ALLOW_CREDENTIALS = True

# corsheaders - A list of origins that are authorized to make cross-site HTTP requests. The origins in this setting will be allowed,
# and the requesting origin will be echoed back to the client in the access-control-allow-origin header. Defaults to [].
CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://sub.example.com",
    "http://localhost:8080",
    "http://127.0.0.1:9000",
    "http://your_wildfly_ip_or_domain:port"
]

# CSRF Integration
# Most sites will need to take advantage of the Cross-Site Request Forgery protection that Django offers. CORS and CSRF are separate, 
# and Django has no way of using your CORS configuration to exempt sites from the Referer checking that it does on secure requests. 
# The way to do that is with its CSRF_TRUSTED_ORIGINS setting. 
CSRF_TRUSTED_ORIGINS = [
    "https://example.com",
    "https://sub.example.com",
    "http://localhost:8080",
    "http://127.0.0.1:9000",
    "http://your_wildfly_ip_or_domain:port"
]

# ========================================================== SECURITY SECTION ==================================================================

# ========================================================== DJANGO CORE SECTION ===============================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True  # Custom added
USE_TZ = True

# Application definition

INSTALLED_APPS = [
    # These applications are included by default as a convenience for the common case.
    "django.contrib.admin",  # The admin site
    "django.contrib.auth",  # An authentication system.
    "django.contrib.contenttypes",  # A framework for content types.
    "django.contrib.sessions",  # A session framework.
    "django.contrib.messages",  # A messaging framework.
    "django.contrib.staticfiles",  # A framework for managing static files.
    
    # Dependent apps
    "django.contrib.postgres",
    "oauth2_provider",
    
    # -------------- BELOW APPS FOR DIFFERENT VARIETIES OF UI FOR BACKEND DRF ---------------------- #
    # NOTE - To use rest_wind
    # rename "templates\rest_framework\api1.html" to "templates\rest_framework\api.html"
    # rename "templates\rest_framework\login1.html" to "templates\rest_framework\login.html"
    "rest_wind", 
    
    "drf_redesign", 
    
    "drf_material",
    # -------------- BELOW APPS FOR DIFFERENT VARIETIES OF UI FOR BACKEND DRF ---------------------- #
    
    "rest_framework",
    "rest_framework.authtoken",
    "encrypted_model_fields",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    "auditlog",
    "crispy_forms",
    "crispy_bootstrap4",
    "drf_spectacular_sidecar",
    
    # Custom apps
    "app1.apps.App1Config",
    "app2.apps.App2Config",
]

MIDDLEWARE = [
    # Middleware - corsheaders, should be placed as high as possible, especially before any middleware that can generate responses
    # such as Django’s CommonMiddleware or Whitenoise’s WhiteNoiseMiddleware. If it is not before, it will not be able to add the
    # CORS headers to these responses.
    "corsheaders.middleware.CorsMiddleware",
    
    # Default middleware coming from  Django
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
    # django-auditlog middleware
    "auditlog.middleware.AuditlogMiddleware",
]

ROOT_URLCONF = "demo_app.urls"

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    
    # 'DjangoModelPermissionsOrAnonReadOnly' only works on views that are tied to a model
    # via.queryset or .get_queryset() (typically GenericAPIView / ViewSets).
    # "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly",], 
    
    # Custom added permission class
    "DEFAULT_PERMISSION_CLASSES" : ["rest_framework.permissions.IsAuthenticated", ],
    
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.FormParser", 
        "rest_framework.parsers.MultiPartParser", 
        
        # Add below for allowing media-type as JSON else we will get this error - "Unsupported Media Type: /question/"
        "rest_framework.parsers.JSONParser",), 
    
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    
    "PAGE_SIZE": 10,
}

SPECTACULAR_SETTINGS = {
    "TITLE" : "Django Starter API",
    "DESCRIPTION" : "API for Django Starter as Example",
    "VERSION" : "1.0.0",
    "SERVE_INCLUDE_SCHEMA" : False,
    "SWAGGER_UI_DIST" : "SIDECAR",  # shorthand to use the sidecar instead
    "SWAGGER_UI_FAVICON_HREF" : "SIDECAR", 
    "REDOC_DIST" : "SIDECAR",
    # OTHER SETTINGS
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR, path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "demo_app.wsgi.application"

CRISPY_ALLOWED_TEMPLATES_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"

# AUDITLOG_INCLUDE_ALL_MODELS
# You can use this setting to register all your models:
AUDITLOG_INCLUDE_ALL_MODELS = True

# AUDITLOG_EXCLUDE_TRACKING_FIELDS
# You can use this setting to exclude named fields from ALL models. This is useful when lots of models share similar
# fields like "created_by", "modified_by" and you want to exclude those from logging. It will be considered when 
# AUDITLOG_INCLUDE_ALL_MODELS = True
AUDITLOG_EXCLUDE_TRACKING_FIELDS = ("created_by", "modified_by")

# AUDITLOG_DISABLE_REMOTE_ADDR
# When using middleware - "AuditlogMiddleware", the IP address is logged by default, you can use this settings to exclude 
# the IP address from logging. It will be considered when AUDITLOG_DISABLE_REMOTE_ADDR  is True.
AUDITLOG_DISABLE_REMOTE_ADDR = True

# AUDITLOG_MASK_TRACKING_FIELDS
# You can use this setting to mask specific field values in all tracked models while still logging changes. This is useful
# when models contain sensitive fields like password, api_key, or secret_token that should not be logged in plain text but 
# need to be auditable.
# When a masked field changes, its values will be replaced with a masked representation (e.g., ****) in the audit log instead
# of storing the actual value.
# This setting will be applied only when AUDITLOG_INCLUDE_ALL_MODELS is True.
AUDITLOG_MASK_TRACKING_FIELDS = ("created_date", "api_key")

# ========================================================== DJANGO CORE SECTION ===============================================================

# ========================================================== DATABASE SECTION ==================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DB_USER_NAME = environ.get("DB_USER_NAME", "").strip()
DB_PWD = environ.get("DB_PWD", "").strip()
DB_NAME = environ.get("DB_NAME", "").strip()
DB_HOST = environ.get("DB_HOST", "").strip()
DB_PORT = environ.get("DB_PORT", "").strip()
DB_SCHEMA_NAME = environ.get("DB_SCHEMA_NAME", "").strip()

DATABASES = {
    "default" : {
        "ENGINE" : "django.db.backends.postgresql",
        "NAME" : DB_NAME,
        "OPTIONS" : {"options" : f"-c search_path={DB_SCHEMA_NAME}"},
        "USER" : DB_USER_NAME,
        "PASSWORD" : DB_PWD,
        "HOST" : DB_HOST,
        "PORT" : DB_PORT,
        # If True, this will cause commit to DB only if all actions for a given web request are successful
        "ATOMIC_REQUESTS" : False,
    }
}

SETUP_TESTDB = False
LOAD_FIXTURES = True

# ========================================================== DATABASE SECTION ==================================================================


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

