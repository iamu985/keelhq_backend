class KeelException(Exception):
    """Base exception for Keel application."""

    status_code: int = 500
    error_code: str = "INTERNAL_SERVER_ERROR"
    default_message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


class DomainError(KeelException):
    """Base exception for domain related errors."""

    status_code: int = 400
    error_code: str = "DOMAIN_ERROR"
    default_message: str = "Business rule violation."


class InfrastructureError(KeelException):
    """Base exception for infrastructure related errors."""

    status_code: int = 500
    error_code: str = "INFRASTRUCTURE_ERROR"
    default_message: str = "Infrastructure error."


class ApplicationError(KeelException):
    """Base exception class for all application related errors."""

    status_code: int = 400
    error_code: str = "APPLICATION_ERROR"
    default_message: str = "Application error."
