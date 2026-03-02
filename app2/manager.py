# Python base imports - Default ones

# Dependent software imports
from django.contrib.auth.base_user import BaseUserManager

# Custom created imports


class CustomUserManager(BaseUserManager):
    """
    Custom Manager for AppUser.

    WHAT IS A MANAGER?

    In Django:
    - A Manager controls how model objects are created and retrieved.
    - It is the interface between Django and the database.

    WHY DO WE NEED A CUSTOM MANAGER?

    Because:
    - We removed 'username'
    - We use 'employee_id' as the login field
    - Django's default UserManager expects 'username'

    So we must define how users and superusers are created.
    """
    # Required so Django can serialize manager in migrations
    use_in_migrations = True

    # ============================================================
    # Create Normal User
    # ============================================================
    def create_user(self, employee_id, password = None, **extra_fields):
        """
        Creates and saves a regular user.

        This method is used by:
        - Django admin
        - createsuperuser command (internally calls create_user)
        - Any manual user creation in code

        IMPORTANT DESIGN DECISION:
        - This method does NOT contain security logic.
        - It delegates password and secret answer handling
          to the model (Single Source of Truth principle).
        """

        # ----------------------------
        # Basic Validations
        # ----------------------------
        if not employee_id:
            raise ValueError("Employee ID must be provided")
        if not password:
            raise ValueError("Password must be provided")
        
        # Normalize email (lowercase domain part)
        email = extra_fields.get("email")
        if not email:
            raise ValueError("Email must be provided")  
        
        # Normalize email (lowercase domain part)
        extra_fields["email"] = self.normalize_email(email)

        # ------------------------------------------------
        # Create user instance (NOT saved yet)
        # ------------------------------------------------
        user = self.model(employee_id = employee_id, **extra_fields)

        # ------------------------------------------------
        # Delegate Password Logic to Model
        # ------------------------------------------------
        # This ensures:
        # - Password hashing
        # - Password history enforcement
        # - Metadata updates
        user.change_password(password)

        # ------------------------------------------------
        # Delegate Secret Answer Logic to Model
        # ------------------------------------------------
        secret_answer = extra_fields.get("secret_answer")
        
        if secret_answer:
            # Hashing happens inside model
            user.set_secret_answer(secret_answer)
        
        # ------------------------------------------------
        # Save to Database
        # ------------------------------------------------
        user.save(using = self._db)
        return user


    # ============================================================
    # Create Superuser
    # ============================================================
    def create_superuser(self, employee_id, password = None, **extra_fields):
        """
        Creates and saves a superuser.

        Called when running:
            python manage.py createsuperuser

        A superuser must have:
        - is_staff = True
        - is_superuser = True
        - is_active = True
        """

        # Ensure required permission flags
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # Safety checks (prevents misconfiguration)
        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")
        
        # Reuse create_user logic (avoids duplication)
        return self.create_user(employee_id, password, **extra_fields)