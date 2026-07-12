from app.exceptions import DomainError


class IdentityError(DomainError):
    """Base exception for identity-related operations."""

    status_code: int = 400
    error_code: str = "IDENTITY_ERROR"
    default_message: str = "Identity operation failed."
