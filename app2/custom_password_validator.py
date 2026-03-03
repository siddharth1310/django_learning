# Python base imports - Default ones
from typing import Optional
from re import search as re_search

# Dependent software imports
from django.utils.translation import gettext
from django.core.exceptions import ValidationError

# Custom created imports
from _utils.models import GlobalAppConfig


class AppPasswordValidator:
    """
    🎛️ ENTERPRISE PASSWORD POLICY ENFORCEMENT
    
    ✅ DYNAMIC RULES (Admin configurable):
        • Min/max length
        • Uppercase/lowercase/numeric/special requirements
        • Custom special character set
        • Username similarity check
    
    🔄 HOW IT WORKS:
    1. __init__() → Cache ALL config values (1-time setup)
    2. validate() → Check password against cached rules
    3. get_help_text() → Dynamic help text for forms
    
    🚀 PERFORMANCE: Zero DB queries per validation!
    """
    
    def __init__(self):
        """
        🚀 ONE-TIME SETUP (Runs when Django loads validators)
        
        WHY CACHE HERE?
            • Password validation called 1000s times/session
            • Avoid 10x DB queries per user registration
            • ConfigManager already cached → Double fast! ⚡
        """

        # 📊 Load ALL security configs (cached by SecurityConfigManager!)
        self.password_min_length = int(GlobalAppConfig.objects.get(category = "security", name = "password_min_length").value)
        self.password_max_length = int(GlobalAppConfig.objects.get(category = "security", name = "password_max_length").value)
        self.require_uppercase = GlobalAppConfig.objects.get(category = "security", name = "require_uppercase").value
        self.require_lowercase = GlobalAppConfig.objects.get(category = "security", name = "require_lowercase").value
        self.require_numeric = GlobalAppConfig.objects.get(category = "security", name = "require_numeric").value
        self.require_special = GlobalAppConfig.objects.get(category = "security", name = "require_special").value
        self.special_characters = GlobalAppConfig.objects.get(category = "security", name = "special_characters").value
        self.help_special = "!, @, #, $, %, ^, &, *, (, ), _, +, -, <, >, =, ~"

    # ====================================== CORE VALIDATION ======================================
    def validate(self, password : str, user : Optional[object] = None) -> None:
        """
        🔍 MAIN VALIDATION LOGIC (Called by Django on every password)
        
        ORDER MATTERS (user-friendly):
        1. Length checks (fastest)
        2. Username similarity  
        3. Character requirements
        4. Max length (last)
        
        RAISES ValidationError → Django shows to user automatically
        """

        # 📏 LENGTH VALIDATION (Fastest checks first)
        if self.password_min_length and len(password) < self.password_min_length:
            raise ValidationError(gettext(f"The password should be at least {self.password_min_length} characters long."), code = "password_too_short")

        # 👤 USERNAME SIMILARITY (Custom user model safe)
        if user:
            # 🔒 Safe attribute access (works with any user model)
            username = getattr(user, "username", None)
            if username and username in password:
                raise ValidationError(gettext("The password cannot contain the username."), code = "password_username")
        
        # 🔤 CHARACTER REQUIREMENTS (Regex - super fast!)
        if self.require_uppercase and not re_search("[A-Z]", password):
            raise ValidationError(gettext("The password must contain at least one uppercase letter"), code = "password_uppercase")

        if self.require_lowercase and not re_search("[a-z]", password):
            raise ValidationError(gettext("The password must contain at least one lowercase letter"), code = "password_lowercase")

        if self.require_numeric and not re_search("[0-9]", password):
            raise ValidationError(gettext("The password must contain at least one numeric character"), code = "password_numeric")

        if self.require_special and not re_search(self.special_characters, password):
            raise ValidationError(gettext(f"The password must contain at least one special character from: {self.help_special}"), code = "password_special")

        # 📏 MAX LENGTH (Last check)
        if self.password_max_length and len(password) > self.password_max_length:
            raise ValidationError(gettext(f"The password should be less than {self.password_max_length} characters long."), code = "password_too_long")


    # ====================================== USER HELP TEXT ======================================
    def get_help_text(self) -> str:
        """
        📋 DYNAMIC FORM HELP TEXT
        
        Django calls this for:
            • Registration forms
            • Password change forms
            • Admin interfaces
        
        SMART: Only shows REQUIRED rules!
        """
        required_parts = []

        if self.require_uppercase:
            required_parts.append("one uppercase")
        
        if self.require_lowercase:
            required_parts.append("one lowercase")

        if self.require_numeric:
            required_parts.append("one numeric")

        if self.require_special:
           required_parts.append(f"one special from: {self.help_special}")
        
        # 📏 Always include length
        length_text = f"{self.password_min_length}-{self.password_max_length} characters"

        if required_parts:
            rules_text = f"{length_text} + {' and '.join(required_parts)}"
        else:
            rules_text = length_text

        return gettext(f"Your password must contain at least {rules_text}.")