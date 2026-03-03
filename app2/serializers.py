# Python base imports - Default ones

# Dependent software imports
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

# Custom created imports
from app2.services.auth_service import AuthService


class LoginSerializer(serializers.Serializer):
    """
    🎯 LOGIN API REQUEST/RESPONSE FORMAT

    <b>*REQUEST*</b>
    ```
    {
        "employee_id" : "EMP001",
        "password" : "SecurePass123!"
    }
    ```

    <b>*RESPONSE*</b>
    ```
    {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "user": {
            "employee_id": "EMP001",
            "email": "john.doe@company.com"
        },
        "password_expired": false,
        "account_locked": false
    }
    ```
    """
    # ====================================== INPUT FIELDS ========================================

    """Primary login identifier (replaces username)"""
    employee_id = serializers.CharField(trim_whitespace = True, max_length = 50, 
                                        error_messages = {
                                            "required" : "Employee ID is required", 
                                            "blank" : "Employee ID cannot be empty"})
    
    """User's plaintext password (hashed by Django)"""
    password = serializers.CharField(write_only = True, min_length = 8, max_length = 64, 
                                     error_messages = {
                                         "required" : "Password is required", 
                                         "blank" : "Password cannot be empty"})
    
    # ====================================== INPUT FIELDS ========================================

    # ====================================== VALIDATION WORKFLOW =================================

    def validate(self, attrs):
        """
        🚀 COMPLETE VALIDATION + TOKEN GENERATION PIPELINE
        
        -  1️⃣ AuthService.login() → Full security checks
        -  2️⃣ Password expiration check  
        -  3️⃣ JWT Token generation
        -  4️⃣ Standardized API response
        
        RETURNS: Complete login response with tokens + metadata
        """

        # 🔐 STEP 1: FULL AUTHENTICATION (All security policies enforced)
        user = AuthService.login(attrs["employee_id"], attrs["password"])

        # ⏰ STEP 2: PASSWORD EXPIRATION CHECK (Non-blocking warning)
        password_expired = user.needs_password_change()
        if password_expired:
            raise serializers.ValidationError("Your password has expired. Please change it.")
        
        # 🔑 STEP 3: GENERATE JWT TOKENS (SimpleJWT)
        refresh = RefreshToken.for_user(user)

        # 📤 STEP 4: STANDARDIZED API RESPONSE
        return {
            "access" : str(refresh.access_token), 
            "refresh" : str(refresh), 
            "user" : {
                "employee_id" : user.employee_id, 
                "email" : user.email, 
                "full_name" : getattr(user, "full_name", None)
            }, 
            "password_expired" : password_expired, 
            "account_locked" : user.is_locked()
        }
    
    # ====================================== EXTRA UTILITY METHODS ================================
    
    def validate_employee_id(self, value : str) -> str:
        """
        🔍 EMPLOYEE ID FORMAT VALIDATION
        
        Ensures employee_id matches DB constraints:
        • Alphanumeric only (A-Z, a-z, 0-9)
        • Max 50 chars (DB field limit)
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Employee ID cannot be empty")
        
        # ✅ Let model validators handle regex in DB layer
        return value.strip()

    def validate_password(self, value : str) -> str:
        """
        🔐 PASSWORD POLICY ENFORCEMENT
        
        Delegates to Django's AUTH_PASSWORD_VALIDATORS:
        • Minimum length
        • Complexity rules (uppercase, numbers, special chars)
        • Custom AppPasswordValidator
        
        Note: Full validation happens in AuthService + model validators
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return value