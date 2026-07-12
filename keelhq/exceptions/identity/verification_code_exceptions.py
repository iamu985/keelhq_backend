from .base import IdentityError


class VerificationCodeGenerationError(IdentityError):
    """Raised when unable to generate a unique verification code after multiple attempts."""

    pass


class VerificationCodeExpiredError(IdentityError):
    """Raised when attempting to use an expired verification code."""

    pass


class VerificationCodeAlreadyUsedError(IdentityError):
    """Raised when attempting to use a verification code that has already been used."""

    pass


class VerificationCodeNotFoundError(IdentityError):
    """Raised when attempting to verify a non-existent verification code."""

    pass
