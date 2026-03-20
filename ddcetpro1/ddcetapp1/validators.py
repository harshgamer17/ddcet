import re
from django.core.exceptions import ValidationError


class CustomPasswordValidator:

    def validate(self, password, user=None):

        # Minimum length check
        if len(password) < 8:
            raise ValidationError(
                "Password must be at least 8 characters long."
            )

        # At least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                "Password must contain at least one uppercase letter."
            )

        # At least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                "Password must contain at least one lowercase letter."
            )

        # At least one digit
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                "Password must contain at least one numeric digit."
            )

        # At least one special character
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>_\-+=/]', password):
            raise ValidationError(
                "Password must contain at least one special character."
            )

    def get_help_text(self):
        return (
            "Your password must contain at least 8 characters, "
            "including one uppercase letter, one lowercase letter, "
            "one number, and one special character."
        )