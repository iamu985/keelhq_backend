"""
Verification service for email OTP authentication.

Responsibility:
- Generate and validate 6-digit verification codes for email-based authentication.
- Ensure code uniqueness, expiration handling, and usage tracking.
- Provide secure verification workflows for user identity confirmation.
"""

import secrets
from datetime import UTC, datetime
from uuid import UUID

from app.core.logger import logger
from app.db.models import VerificationCode
from app.exceptions.identity import (
    VerificationCodeExpiredError,
    VerificationCodeGenerationError,
    VerificationCodeNotFoundError,
)
from app.repositories.identity.verification_repository import VerificationCodeRepository


class VerificationService:
    """
    Service layer for managing verification codes in email OTP workflows.

    This service handles the complete lifecycle of verification codes including
    generation, validation, expiration checking, and usage tracking. It ensures
    security through cryptographically secure random generation and proper
    uniqueness validation.

    Attributes:
        repository: Data access layer for verification code operations.
    """

    def __init__(self, repository: VerificationCodeRepository) -> None:
        self.repository = repository

    async def generate_verification_code(self, local_user_id: UUID) -> VerificationCode:
        """
        Generate a unique 6-digit verification code for the specified user.

        This method creates a cryptographically secure 6-digit code and ensures
        its uniqueness in the system. It implements retry logic to handle the
        rare case of code collisions.

        Args:
            local_user_id: The UUID of the user for whom to generate the code.

        Returns:
            VerificationCode: The created verification code entity.

        Raises:
            VerificationCodeGenerationError: If unable to generate a unique code
                after 10 attempts.

        Example:
            >>> code = await service.generate_verification_code(user.id)
            >>> print(f"Generated code: {code.code}")
            Generated code: 123456
        """
        logger.info(f"Generating verification code for user: {local_user_id}")

        max_attempts = 10
        for attempt in range(max_attempts):
            # Generate cryptographically secure 6-digit code
            code_value = secrets.choice(range(100000, 1000000))
            logger.debug(f"Attempt {attempt + 1}: Generated code {code_value}")

            # Check for uniqueness
            existing_code = await self.repository.get_by_code(code_value)
            if existing_code is None:
                # Code is unique, create and return
                verification_code = VerificationCode(code=code_value, local_user_id=local_user_id)
                created_code = await self.repository.create(verification_code)
                logger.info(f"Successfully created verification code: {created_code.id}")
                return created_code

            logger.warning(f"Code collision detected: {code_value}, retrying...")

        # If we reach here, we couldn't generate a unique code
        error_msg = f"Failed to generate unique verification code after {max_attempts} attempts"
        logger.error(error_msg)
        raise VerificationCodeGenerationError(error_msg)

    async def verify_code(self, local_user_id: UUID, code: int) -> VerificationCode:
        """
        Verify a 6-digit code for the specified user.

        This method performs comprehensive validation including:
        - Code existence and user association
        - Usage status (must be unused)
        - Expiration status (must not be expired)

        Args:
            local_user_id: The UUID of the user attempting verification.
            code: The 6-digit verification code to validate.

        Returns:
            VerificationCode: The validated verification code entity.

        Raises:
            VerificationCodeNotFoundError: If the code doesn't exist or isn't
                associated with the specified user.
            VerificationCodeAlreadyUsedError: If the code has already been used.
            VerificationCodeExpiredError: If the code has expired.

        Example:
            >>> try:
            ...     verified = await service.verify_code(user.id, 123456)
            ...     print("Code verified successfully")
            ... except VerificationCodeExpiredError:
            ...     print("Code has expired")
        """
        logger.info(f"Verifying code {code} for user: {local_user_id}")

        # Find the unused code for the user
        verification_code = await self.repository.get_unused_code_for_user(local_user_id, code)

        if verification_code is None:
            logger.warning(f"Invalid or used verification code: {code} for user: {local_user_id}")
            raise VerificationCodeNotFoundError(f"Invalid or used verification code: {code}")

        # Check expiration
        if self.is_code_expired(verification_code):
            logger.warning(f"Expired verification code: {code} for user: {local_user_id}")
            raise VerificationCodeExpiredError(f"Verification code has expired: {code}")

        logger.info(f"Successfully verified code: {code} for user: {local_user_id}")
        return verification_code

    def is_code_expired(self, verification_code: VerificationCode) -> bool:
        """
        Check if a verification code has expired.

        Args:
            verification_code: The verification code to check.

        Returns:
            bool: True if the code is expired, False otherwise.

        Example:
            >>> if service.is_code_expired(code):
            ...     print("Code is no longer valid")
        """
        now = datetime.now(UTC)
        is_expired = verification_code.expires_at < now

        logger.debug(
            f"Code expiration check - Code: {verification_code.code}, "
            f"Expires: {verification_code.expires_at}, Now: {now}, "
            f"Expired: {is_expired}"
        )

        return is_expired

    async def mark_code_as_used(self, verification_code: VerificationCode) -> VerificationCode:
        """
        Mark a verification code as used.

        This method atomically updates the verification code to prevent
        reuse and maintains the integrity of the verification workflow.

        Args:
            verification_code: The verification code to mark as used.

        Returns:
            VerificationCode: The updated verification code entity.

        Example:
            >>> used_code = await service.mark_code_as_used(verified_code)
            >>> assert used_code.is_used == True
        """
        logger.info(f"Marking verification code as used: {verification_code.id}")

        if verification_code.is_used:
            logger.warning(f"Code already marked as used: {verification_code.id}")
            return verification_code

        updated_code = await self.repository.mark_as_used(verification_code)
        logger.info(f"Successfully marked code as used: {updated_code.id}")
        return updated_code

    async def verify_and_consume_code(self, local_user_id: UUID, code: int) -> VerificationCode:
        """
        Verify a code and mark it as used in a single atomic operation.

        This is a convenience method that combines verification and usage
        tracking, commonly used in authentication workflows.

        Args:
            local_user_id: The UUID of the user attempting verification.
            code: The 6-digit verification code to validate and consume.

        Returns:
            VerificationCode: The verified and consumed verification code.

        Raises:
            VerificationCodeNotFoundError: If the code doesn't exist or is invalid.
            VerificationCodeAlreadyUsedError: If the code has already been used.
            VerificationCodeExpiredError: If the code has expired.

        Example:
            >>> try:
            ...     result = await service.verify_and_consume_code(user.id, 123456)
            ...     print("Authentication successful")
            ... except VerificationCodeExpiredError:
            ...     print("Please request a new code")
        """
        logger.info(f"Verifying and consuming code {code} for user: {local_user_id}")

        # First verify the code
        verified_code = await self.verify_code(local_user_id, code)

        # Then mark it as used
        consumed_code = await self.mark_code_as_used(verified_code)

        logger.info(f"Successfully verified and consumed code: {code}")
        return consumed_code
