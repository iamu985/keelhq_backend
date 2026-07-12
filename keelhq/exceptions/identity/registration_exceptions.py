"""Registration-specific exceptions.

Responsibility:
- Define domain errors raised during the user-registration use case.
"""

from .base import IdentityError


class RegistrationError(IdentityError):
    """Base exception for registration-related errors."""

    status_code: int = 400
    error_code: str = "REGISTRATION_ERROR"
    default_message: str = "Registration failed."


class UsernameAlreadyExistsError(RegistrationError):
    """Raised when a registration request uses an existing username."""

    status_code: int = 409
    error_code: str = "USERNAME_ALREADY_EXISTS"
    default_message: str = "Username already exists."


class EmailAlreadyExistsError(RegistrationError):
    """Raised when a registration request uses an existing email address."""

    status_code: int = 409
    error_code: str = "EMAIL_ALREADY_EXISTS"
    default_message: str = "Email already exists."
