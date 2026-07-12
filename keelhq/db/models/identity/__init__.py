"""Identity domain models.

Responsibility:
- Expose the identity-related database models for import.
"""

from .local_user import LocalUser
from .verification import VerificationCode

__all__ = ["LocalUser", "VerificationCode"]
