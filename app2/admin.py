# Python base imports - Default ones
from typing import cast

# Dependent software imports
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField

# Custom created imports
from app2.models import AppUser

# ============================================================
# Custom User Creation Form (Admin → Add User)
# ============================================================
class AppUserCreationForm(forms.ModelForm):
    """
    This form is used in Django Admin when adding a new user.

    WHY CUSTOM FORM?

    Because:
    - We removed 'username'
    - We use 'employee_id'
    - We want password confirmation (password1 & password2)
    """

    # Two password fields for confirmation
    password1 = forms.CharField(label="Password", widget = forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget = forms.PasswordInput)

    class Meta:
        model = AppUser
        fields = ("employee_id", "email", "first_name", "last_name", "secret_hint", "secret_answer")
    
    # ------------------------------------------------
    # Validate matching passwords
    # ------------------------------------------------
    def clean_password2(self):
        """
        Ensures password1 and password2 match.
        This is UI-level validation only.
        """
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")

        if p1 != p2:
            raise ValidationError("Passwords do not match")

        return p2
    
    # ------------------------------------------------
    # Save user using domain logic
    # ------------------------------------------------
    def save(self, commit = True):
        """
        Important:
        We DO NOT hash passwords here manually.

        We delegate to:
            user.change_password()
            user.set_secret_answer()

        This keeps security logic inside the model.
        """
        user = super().save(commit = False)

        # Delegate password handling to model
        user.change_password(self.cleaned_data["password1"])

        # Delegate secret answer hashing to model
        user.set_secret_answer(self.cleaned_data["secret_answer"])

        if commit:
            user.save()

        return user


# ============================================================
# Custom Password Change Form (Admin → Change Password)
# ============================================================
class AppUserAdminPasswordChangeForm(AdminPasswordChangeForm):
    """
    This form is used when admin clicks:
        "Change password" inside user detail page.

    We override clean_password2 to enforce
    password history policy.

    The actual policy enforcement lives in the model.
    """
    def clean_password2(self) -> str:
        password2 = self.cleaned_data.get("password2")

        if not password2:
            raise ValidationError("Password is required.")
        
        # Tell type checker that self.user is AppUser
        user = cast(AppUser, self.user)

        try:
            # This calls model-level logic
            user.change_password(password2)
        except ValueError as e:
            # Convert domain error into form error
            raise ValidationError(str(e))

        return password2


# ============================================================
# Custom User Change Form (Admin → Edit Existing User)
# ============================================================
class AppUserChangeForm(forms.ModelForm):
    """
    Used when editing an existing user.

    ReadOnlyPasswordHashField:
    - Shows hashed password
    - Prevents editing raw password directly
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = AppUser
        fields = "__all__"


# ============================================================
# Admin Configuration
# ============================================================
@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    """
    This class customizes how AppUser appears in Django Admin.

    We extend Django's built-in UserAdmin.
    """
    model = AppUser

    # Attach custom forms
    form = AppUserChangeForm
    add_form = AppUserCreationForm
    change_password_form = AppUserAdminPasswordChangeForm

    # Default ordering in admin list view
    ordering = ("employee_id",)

    # Filters on right sidebar
    list_filter = ("is_staff", "is_active", "is_superuser")

    # Fields that cannot be edited manually
    readonly_fields = ("last_password_change", "last_passwords")

    # Search box fields
    search_fields = ("employee_id", "email", "first_name", "last_name")

    # Columns shown in user list page
    list_display = ("employee_id", "email", "first_name", "last_name", "is_staff", "is_active", "unsuccessful_attempts")

    # ------------------------------------------------
    # Edit User Page Layout
    # ------------------------------------------------
    fieldsets = (
        (None, {"fields" : ("employee_id", "password")}),
        (_("Personal Info"), {"fields" : ("first_name", "last_name", "full_name", "email")}),
        (_("Security"), {"fields" : ("secret_hint", "secret_answer", "last_password_change", "last_passwords", "unsuccessful_attempts")}),
        (_("Permissions"), {"fields" : ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important Dates"), {"fields" : ("last_login",)}),
    )

    # ------------------------------------------------
    # Add User Page Layout
    # ------------------------------------------------
    add_fieldsets = (
        (None, {
            "classes" : ("wide",), 
            "fields" : ("employee_id", "email", "first_name", "last_name", "secret_hint", "secret_answer", "password1", "password2", "is_staff", "is_superuser", "is_active")
            }),
    )