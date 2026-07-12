"""Registration-specific exceptions.

Responsibility:
- Define domain errors raised during the user-registration use case.
"""

from .base import IdentityError


class UsernameAlreadyExistsError(IdentityError):
    """Raised when a registration request uses an existing username."""

    pass


class EmailAlreadyExistsError(IdentityError):
    """Raised when a registration request uses an existing email address."""

    pass
