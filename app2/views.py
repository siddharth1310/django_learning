# Python base imports - Default ones

# Dependent software imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# Custom created imports
from app2.serializers import LoginSerializer


class LoginAPIView(APIView):
    """
    🔑 LOGIN ENDPOINT
    ----------------
    
    POST /api/auth/login/
    
    ✅ FEATURES:
    - Public endpoint (no auth required)
    - Complete JWT token generation
    - Security policy enforcement
    - Standardized error responses
    
    ✅ SECURITY:
    - Rate limiting (add to urls.py)
    - CSRF exempt (APIView default)
    - Input validation (Serializer)
    - Business logic isolation (AuthService)
    """

    # 🌍 PUBLIC ACCESS - No authentication required
    permission_classes = [AllowAny]

    def post(self, request):
        """
        🎯 LOGIN WORKFLOW EXECUTION
        
        <b>*FLOW*</b>
        1. Create serializer with request data
        2. Run validation (raises 400 on error)  
        3. Return complete login response (tokens + metadata)
        
        <b>*RESPONSES*</b>
        - 200 OK → Login successful + JWT tokens
        - 400 Bad Request → Validation errors
        - 401 Unauthorized → Invalid credentials/locked
        """

        # 📥 STEP 1: SERIALIZER VALIDATION + BUSINESS LOGIC
        serializer = LoginSerializer(data = request.data, context = {"request" : request})

        # 🚫 AUTO-HANDLES ERRORS (400 Bad Request)
        serializer.is_valid(raise_exception = True)

        # 📤 STEP 2: SUCCESS RESPONSE (Already prepared by serializer)
        return Response(serializer.validated_data, status = status.HTTP_200_OK)
    

    # ====================================== OPENAPI/SWAGGER DOCS =================================
    
    @staticmethod
    def get_permission_classes():
        """Explicit permission declaration for API docs"""
        return [AllowAny]
    

    def get_serializer_class(self):
        """Explicit serializer declaration for API docs"""
        return LoginSerializer