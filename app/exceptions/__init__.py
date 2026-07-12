class KeelException(Exception):
    """Base exception for Keel application."""

    pass


class DomainError(KeelException):
    """Base exception for domain related errors"""

    pass


class InfrastructureError(KeelException):
    """Base exception for infrastructure related errors"""

    pass


class ApplicationError(KeelException):
    """Base exception class for all application related errors"""

    pass
