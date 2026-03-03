# Python base imports - Default ones

# Dependent software imports
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import check_password, make_password
from encrypted_model_fields.fields import EncryptedCharField, EncryptedEmailField

# Custom created imports
from app2.manager import CustomUserManager
from app2.config import SecurityConfigManager

class AuditModel(models.Model):
    """
    Abstract base model providing audit trail fields for all business entities.
    
    ✅ KEY FEATURES
        • Automatic timestamps (created/modified)
        • User tracking (who made changes) 
        • Versioning support for optimistic locking
        • NO database table created (abstract=True)
    """
    # Automatically set when record is first created
    created_date = models.DateTimeField(auto_now_add = True, editable = False)

    # Automatically updated every time record is saved
    modified_date = models.DateTimeField(auto_now_add = True, editable = False)

    # Optional version tracking (useful for optimistic locking)
    version = models.PositiveIntegerField(default = 0)

    # Track who created the record (can be auto-populated via middleware later)
    created_by = models.CharField(max_length = 50, default = "admin")

    # Track who last modified the record
    modified_by = models.CharField(max_length = 50, default = "admin")
    
    class Meta:
        # Important: No separate DB table
        abstract = True


class AppUser(AbstractUser, AuditModel): # type: ignore
    """
    🔐 CUSTOM USER MODEL - Enterprise Grade
    
    INHERITANCE:
        • AbstractUser → Django auth features (password hashing, groups, permissions)
        • AuditModel  → Automatic audit trail (created/modified tracking)
    
    🔄 LOGIN FIELD: 
        • `employee_id` REPLACES `username`
    """

    # Remove default username field from AbstractUser
    username = None
    
    # ============================================ CORE IDENTITY FIELDS ===============================================

    # Employee ID becomes our login username
    employee_id = models.CharField(null = False, 
                                   unique = True, 
                                   validators = [RegexValidator(
                                       regex = "^[A-Za-z0-9]+$", 
                                       message = "Employee ID can be alphanumeric only")])
    
    # EncryptedCharField stores encrypted data in DB. This protects PII (Personally Identifiable Information).
    first_name = EncryptedCharField(null = False, 
                                    max_length = 50, 
                                    validators = [RegexValidator(
                                        regex = "^[A-Za-z0-9\\s-]+$", 
                                        message = "First name can contain letters, numbers, spaces or dashes")])
    

    last_name = EncryptedCharField(null = False, 
                                   max_length = 50, 
                                   validators = [RegexValidator(
                                       regex = "^[A-Za-z0-9\\s-]+$", 
                                       message = "First name can contain letters, numbers, spaces or dashes")])

    # Security question hint (encrypted for privacy)
    secret_hint = EncryptedCharField(null = False, max_length = 100)

    """
    💡 HASHED secret answer (NOT encrypted)
    • Hashing = One-way (secure verification only)
    • Encryption = Two-way (reversible = NEVER for secrets)
    """
    secret_answer = models.CharField(max_length = 255)

    # Auto-generated full name (derived field)
    full_name = EncryptedCharField(null = True, max_length = 100)

    # Email stored encrypted for additional protection
    email = EncryptedEmailField(unique = True)

    # ============================================ CORE IDENTITY FIELDS ===============================================

    # ============================================ SECURITY_FIELDS ====================================================
    
    """
    📜 PASSWORD HISTORY
    Stores last N hashed passwords to prevent reuse
    Example: ["pbkdf2_sha256$...", "pbkdf2_sha256$..."]
    """
    last_passwords = models.JSONField(default = list, blank = True)

    # Timestamp of last password change
    last_password_change = models.DateTimeField(default = timezone.now)

    # Count of failed login attempts
    unsuccessful_attempts = models.IntegerField(default = 0)

    # 🎛️ DJANGO AUTH CONFIGURATION
    objects = CustomUserManager() # type: ignore

    # Tell Django to use employee_id for login
    USERNAME_FIELD = "employee_id"

    # Required when creating superuser via createsuperuser
    REQUIRED_FIELDS = ["first_name", "last_name", "secret_hint", "secret_answer", "email"]

    # ============================================ SECURITY_FIELDS ====================================================


    # ====================================== DYNAMIC CONFIG ACCESSORS =================================================

    @classmethod
    def get_max_login_attempts(cls) -> int:
        """🔒 Get max failed login attempts from GlobalAppConfig (default: 3)"""
        return int(SecurityConfigManager.get("auth_retries"))
    
    @classmethod
    def get_password_history_limit(cls) -> int:
        """📜 Get password history limit from GlobalAppConfig (default: 5)"""
        return int(SecurityConfigManager.get("password_limit"))
    
    @classmethod
    def get_password_age_days(cls) -> int:
        """⏰ Get password expiration age from GlobalAppConfig (default: 90 days)"""
        return int(SecurityConfigManager.get("password_age"))
    
    # ====================================== DYNAMIC CONFIG ACCESSORS =================================================

    # ====================================== SECURITY BUSINESS LOGIC ==================================================

    def is_locked(self) -> bool:
        """🔒 Check if account is locked due to excessive failed logins"""
        max_attempts = self.get_max_login_attempts()
        return self.unsuccessful_attempts >= max_attempts
    

    def needs_password_change(self) -> bool:
        """
        ⏰ PASSWORD EXPIRATION CHECK
        Returns True if password age exceeds configured limit
        """
        password_age_days = self.get_password_age_days()
        age_threshold = timezone.now() - timezone.timedelta(days = password_age_days)
        return self.last_password_change < age_threshold
    

    def register_failed_login(self):
        """📈 Increment failed login counter + save efficiently"""
        self.unsuccessful_attempts = self.unsuccessful_attempts + 1
        self.save(update_fields = ["unsuccessful_attempts"])
    

    def is_in_password_history(self, raw_password : str) -> bool:
        """
        🔍 PASSWORD REUSE DETECTION
        Checks if raw_password matches:
        1. Current password
        2. Any stored previous passwords
        """
        # Check current password
        if self.password and check_password(raw_password, self.password):
            return True
        
        # Check history
        return any(check_password(raw_password, old_hash) for old_hash in (self.last_passwords or []))
    

    def change_password(self, raw_password : str):
        """
        🔄 COMPLETE PASSWORD CHANGE WORKFLOW
        SINGLE ENTRY POINT for ALL password changes
        
        ✅ Enforces:
        • Password history policy
        • Secure hashing (Django's PBKDF2)
        • Metadata updates
        • Failed login reset
        """
        # 🚫 Prevent password reuse (skip for new users)
        if self.pk and self.is_in_password_history(raw_password):
            raise ValueError("Cannot reuse recent passwords")

        # 📜 Update history BEFORE changing password
        if self.password:
            history = self.last_passwords or []
            history.append(self.password)
            
            # Keep only configured number of previous passwords
            history_limit = self.get_password_history_limit()
            self.last_passwords = history[-history_limit:]

        # 🔐 Hash & set new password (Django handles this securely)
        super().set_password(raw_password)
        
        # 📊 Update metadata
        self.last_password_change = timezone.now()
        self.unsuccessful_attempts = 0
    
    # ====================================== SECURITY BUSINESS LOGIC ==================================================

    # ====================================== SECRET QUESTION LOGIC ====================================================
    
    def set_secret_answer(self, raw_answer : str):
        """🔐 Hash secret answer (one-way transformation)"""
        self.secret_answer = make_password(raw_answer)

    def check_secret_answer(self, raw_answer : str) -> bool:
        """✅ Verify secret answer against stored hash"""
        return check_password(raw_answer, self.secret_answer)
    
    # ====================================== SECRET QUESTION LOGIC ====================================================

    # ====================================== UTILITY METHODS ==========================================================
    
    def __str__(self) -> str:
        """User-friendly string representation"""
        return self.employee_id

    def save(self, *args, **kwargs):
        """
        🔄 AUTO-GENERATE full_name from first_name + last_name
        Ensures data consistency across the system
        """
        if self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        
        super().save(*args, **kwargs)
    
    # ====================================== UTILITY METHODS ==========================================================

    # ====================================== MODEL META CONFIGURATION =================================================

    class Meta(AuditModel.Meta):
        """
        Extends AuditModel Meta.
        """
        indexes = [models.Index(fields = ["employee_id"])]
        ordering = ["employee_id"]
        db_table = "app_users"
    
    # ====================================== MODEL META CONFIGURATION =================================================