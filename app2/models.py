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


# ============================================================
# AuditModel (Abstract Base Model)
# ============================================================
class AuditModel(models.Model):
    """
    This is an abstract base model. It provides audit-related fields that can be reused
    across multiple models.

    Because 'abstract = True', Django will NOT create a separate database table for this model.
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


# ================================
# App User Model
# ================================
class AppUser(AbstractUser, AuditModel): # type: ignore
    """
    Custom User Model.

    We inherit from:
    - AbstractUser → gives us Django's authentication features
    - AuditModel → gives us created/modified tracking

    We REMOVE username and use employee_id instead.
    """

    # Remove default username field from AbstractUser
    username = None
    
    # ============================================================
    # Core Identity Fields
    # ============================================================

    # Employee ID becomes our login username
    employee_id = models.CharField(null = False, 
                                   unique = True, 
                                   validators = [RegexValidator(regex = "^[A-Za-z0-9]+$", 
                                                                message = "Employee ID can be alphanumeric only")])
    
    # EncryptedCharField stores encrypted data in DB. This protects PII (Personally Identifiable Information).
    first_name = EncryptedCharField(null = False, 
                                    max_length = 50, 
                                    validators = [RegexValidator(regex = "^[A-Za-z0-9\\s-]+$", 
                                                                 message = "First name can contain letters, numbers, spaces or dashes")])
    last_name = EncryptedCharField(null = False, 
                                   max_length = 50, 
                                   validators = [RegexValidator(regex = "^[A-Za-z0-9\\s-]+$", 
                                                                message = "First name can contain letters, numbers, spaces or dashes")])

    # Security question hint (encrypted for privacy)
    secret_hint = EncryptedCharField(null = False, max_length = 100)

    # IMPORTANT:
    # secret_answer is HASHED (not encrypted).
    # We hash it because we should NEVER be able to reverse it.
    secret_answer = models.CharField(max_length = 255)

    # Auto-generated full name (derived field)
    full_name = EncryptedCharField(null = True, max_length = 100)

    # Email stored encrypted for additional protection
    email = EncryptedEmailField(unique = True)

    # ============================================================
    # Security Fields
    # ============================================================
    
    # Stores last N hashed passwords
    # Example: ["pbkdf2_sha256$...", "pbkdf2_sha256$..."]
    last_passwords = models.JSONField(default = list, blank = True)

    # Timestamp of last password change
    last_password_change = models.DateTimeField(default = timezone.now)

    # Count of failed login attempts
    unsuccessful_attempts = models.IntegerField(default = 0)

    # Attach custom manager
    objects = CustomUserManager() # type: ignore

    # Tell Django to use employee_id for login
    USERNAME_FIELD = "employee_id"

    # Required when creating superuser via createsuperuser
    REQUIRED_FIELDS = ["first_name", "last_name", "secret_hint", "secret_answer", "email"]

    # Security policy constants
    MAX_LOGIN_ATTEMPTS = 5
    PASSWORD_HISTORY_LIMIT = 5

    # ============================================================
    # Utility Methods
    # ============================================================
    
    def __str__(self):
        """String representation of user."""
        return str(self.employee_id)

    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate full_name.

        This ensures consistency:
        If first_name or last_name changes,
        full_name updates automatically.
        """
        if self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        
        super().save(*args, **kwargs)

    # ============================================================
    # PASSWORD DOMAIN LOGIC (Single Source of Truth)
    # ============================================================

    def is_in_password_history(self, raw_password : str) -> bool:
        """
        Check whether the provided password matches:

        1) Current password
        2) Any of the previously stored passwords

        check_password() safely compares raw password
        with hashed password.
        """

        # Check current password
        if self.password and check_password(raw_password, self.password):
            return True
        
        # Check previous passwords
        return any(
            check_password(raw_password, old_password) 
            for old_password in (self.last_passwords or [])
        )

    def change_password(self, raw_password : str):
        """
        Domain-level password change entry point.

        WHY THIS METHOD EXISTS:
        - Enforces password history policy
        - Handles hashing
        - Updates password metadata
        - Resets failed login counter

        All password changes should go through this method.
        """

        # Prevent reuse (only check for existing users)
        if self.pk and self.is_in_password_history(raw_password):
            raise ValueError("You cannot reuse a previous password.")

        # Save current password into history (before changing)
        if self.password:
            history = self.last_passwords or []
            history.append(self.password)

            # Keep only last N passwords
            self.last_passwords = history[-self.PASSWORD_HISTORY_LIMIT :]
        
        # Use Django's built-in secure hashing
        super().set_password(raw_password)

        # Update metadata
        self.last_password_change = timezone.now()

        # Reset failed login attempts
        self.unsuccessful_attempts = 0

    # ============================================================
    # SECRET ANSWER DOMAIN LOGIC
    # ============================================================

    def set_secret_answer(self, raw_answer : str):
        """
        Hash the secret answer.

        We hash instead of encrypt because:
        - We should never need to reverse it.
        - We only need to verify it.
        """
        self.secret_answer = make_password(raw_answer)

    def check_secret_answer(self, raw_answer : str) -> bool:
        """
        Validate secret answer by comparing
        raw input with stored hashed value.
        """
        return check_password(raw_answer, self.secret_answer)

    # ============================================================
    # ACCOUNT LOCK LOGIC
    # ============================================================

    def register_failed_login(self):
        """
        Increment failed login counter.
        Call this inside authentication backend
        when login fails.
        """
        self.unsuccessful_attempts = self.unsuccessful_attempts + 1
        self.save(update_fields = ["unsuccessful_attempts"])

    def is_locked(self) -> bool:
        """
        Check whether account should be locked
        based on maximum allowed failed attempts.
        """
        return self.unsuccessful_attempts >= self.MAX_LOGIN_ATTEMPTS
    
    # ============================================================
    # Model Meta Configuration
    # ============================================================

    class Meta(AuditModel.Meta):
        """
        Extends AuditModel Meta.
        """
        indexes = [models.Index(fields = ["employee_id"])]
        ordering = ["employee_id"]
        db_table = "app_users"