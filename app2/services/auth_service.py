# Python base imports - Default ones

# Dependent software imports
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework.exceptions import AuthenticationFailed

# Custom created imports
from app2.models import AppUser


class AuthService:
    """
    🎯 CENTRAL AUTHENTICATION ORCHESTRATOR
    
    WHY THIS CLASS EXISTS:
    - Encapsulates ALL login complexity
    - Enforces security policies consistently
    - Makes views/serializers super thin
    - Easy to test/mock in isolation
    """
    
    @staticmethod
    def login(employee_id : str, password : str):
        """
        🔑 COMPLETE LOGIN WORKFLOW
        ==========================
        
        STEP-BY-STEP PROCESS:
        1. Fetch user by employee_id
        2. Check account lock status  
        3. Django authenticate() → password verification
        4. Register failed attempt (if needed)
        5. Reset counters on success
        6. Update last_login timestamp
        7. Return authenticated user
        
        RAISES:
        - AuthenticationFailed → Invalid credentials
        - AuthenticationFailed → Account locked
        """

        # 🚀 STEP 1: LOCATE USER
        try:
            user = AppUser.objects.get(employee_id = employee_id)
        except AppUser.DoesNotExist:
            # 💡 NEVER reveal if user exists (security best practice)
            raise AuthenticationFailed("Invalid credentials")

        # 🔒 STEP 2: CHECK ACCOUNT LOCKOUT (Dynamic Config)
        if user.is_locked():
            raise AuthenticationFailed(f"Account locked after {user.get_max_login_attempts()} failed attempts. Contact administrator to unlock.")

        # ✅ STEP 3: DJANGO PASSWORD VERIFICATION
        # Uses PBKDF2 hashing + timing-attack resistance
        authenticated_user = authenticate(employee_id = employee_id, password = password)

        if not authenticated_user:
            # 📈 STEP 4: REGISTER FAILED ATTEMPT
            user.register_failed_login()

            # 💡 Don't reveal attempt count (security)
            raise AuthenticationFailed("Invalid credentials")

        # 🎉 STEP 5: SUCCESS - CLEANUP & AUDIT
        user.unsuccessful_attempts = 0  # Reset counter
        user.save(update_fields = ["unsuccessful_attempts"])  # Efficient update

        # 📅 STEP 6: DJANGO LAST LOGIN AUDIT
        update_last_login(AppUser, user)

        # ✅ STEP 7: RETURN SUCCESSFUL USER
        return user
    
    
    @staticmethod
    def verify_employee_exists(employee_id : str) -> bool:
        """
        🔍 QUICK EMPLOYEE LOOKUP (No password check)
        
        USE CASES:
        • Password reset flow
        • Profile exists check
        • Account recovery
        
        RETURNS: True if employee_id exists
        """
        return AppUser.objects.filter(employee_id = employee_id).exists()
    

    @staticmethod
    def unlock_account(user : AppUser) -> None:
        """
        🔓 ADMIN-ONLY: Reset failed attempts counter
        
        USE CASE: Helpdesk unlocks locked accounts
        """
        user.unsuccessful_attempts = 0
        user.save(update_fields = ["unsuccessful_attempts"])
    
    
    @staticmethod
    def get_account_status(employee_id : str) -> dict:
        """
        📊 ACCOUNT STATUS INSPECTION (Admin/Security)
        
        RETURNS:
        {
            "exists": true/false,
            "is_locked": true/false,
            "failed_attempts": 3,
            "max_attempts": 5,
            "password_age_days": 45  # days since last change
        }
        """
        try:
            user = AppUser.objects.get(employee_id = employee_id)
            return {
                "exists" : True, 
                "is_locked" : user.is_locked(), 
                "failed_attempts" : user.unsuccessful_attempts, 
                "max_attempts" : user.get_max_login_attempts(), 
                "password_expired" : user.needs_password_change(), 
                "password_age_days" : (timezone.now() - user.last_password_change).days
            }
        except AppUser.DoesNotExist:
            return {"exists" : False}
