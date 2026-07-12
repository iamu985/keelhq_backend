"""Tests for VerificationService.

Responsibility:
- Verify all business logic operations on VerificationService using mocked
  dependencies to ensure fast, isolated unit testing of the service layer.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from keelhq.db.models import VerificationCode
from keelhq.exceptions.identity import (
    VerificationCodeExpiredError,
    VerificationCodeGenerationError,
    VerificationCodeNotFoundError,
)
from keelhq.repositories.identity.verification_repository import VerificationCodeRepository
from keelhq.services.verification_service import VerificationService


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Return a mocked VerificationCodeRepository."""
    return AsyncMock(spec=VerificationCodeRepository)


@pytest.fixture
def verification_service(mock_repository: AsyncMock) -> VerificationService:
    """Return a VerificationService backed by the mocked repository."""
    return VerificationService(repository=mock_repository)


@pytest.fixture
def sample_user_id() -> UUID:
    """Return a deterministic user ID for testing."""
    return UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def sample_verification_code(sample_user_id: UUID) -> VerificationCode:
    """Return a deterministic VerificationCode instance for assertions."""
    return VerificationCode(
        id=uuid4(),
        code=123456,
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
        is_used=False,
        local_user_id=sample_user_id,
    )


@pytest.fixture
def expired_verification_code(sample_user_id: UUID) -> VerificationCode:
    """Return an expired VerificationCode instance for testing."""
    return VerificationCode(
        id=uuid4(),
        code=654321,
        expires_at=datetime.now(UTC) - timedelta(minutes=1),  # Expired
        is_used=False,
        local_user_id=sample_user_id,
    )


@pytest.fixture
def used_verification_code(sample_user_id: UUID) -> VerificationCode:
    """Return a used VerificationCode instance for testing."""
    return VerificationCode(
        id=uuid4(),
        code=111111,
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
        is_used=True,  # Already used
        local_user_id=sample_user_id,
    )


@pytest.mark.asyncio
async def test_generate_verification_code_success(
    verification_service: VerificationService,
    mock_repository: AsyncMock,
    sample_user_id: UUID,
) -> None:
    """generate_verification_code should create and return a unique code."""
    # Mock repository to return None for uniqueness check (code is unique)
    mock_repository.get_by_code.return_value = None

    # Mock the create method to return the created code
    created_code = MagicMock()
    mock_repository.create.return_value = created_code

    result = await verification_service.generate_verification_code(sample_user_id)

    assert result is created_code
    mock_repository.get_by_code.assert_called_once()
    mock_repository.create.assert_called_once()

    # Verify the created code has the correct user ID
    call_args = mock_repository.create.call_args[0][0]
    assert call_args.local_user_id == sample_user_id
    assert 100000 <= call_args.code <= 999999  # 6-digit code


@pytest.mark.asyncio
async def test_generate_verification_code_collision_retry(
    verification_service: VerificationService,
    mock_repository: AsyncMock,
    sample_user_id: UUID,
) -> None:
    """generate_verification_code should retry on code collision."""
    # First call returns existing code (collision), second returns None (unique)
    mock_repository.get_by_code.side_effect = [MagicMock(), None]

    created_code = MagicMock()
    mock_repository.create.return_value = created_code

    result = await verification_service.generate_verification_code(sample_user_id)

    assert result is created_code
    assert mock_repository.get_by_code.call_count == 2
    mock_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_verification_code_max_attempts_exceeded(
    verification_service: VerificationService,
    mock_repository: AsyncMock,
    sample_user_id: UUID,
) -> None:
    """generate_verification_code should raise error after max attempts."""
    # Always return existing code (collision)
    mock_repository.get_by_code.return_value = MagicMock()

    with pytest.raises(VerificationCodeGenerationError) as exc_info:
        await verification_service.generate_verification_code(sample_user_id)

    assert "Failed to generate unique verification code after 10 attempts" in str(exc_info.value)
    assert mock_repository.get_by_code.call_count == 10
    mock_repository.create.assert_not_called()


@pytest.mark.asyncio
async def test_verify_code_success(
    verification_service: VerificationService,
    mock_repository: AsyncMock,
    sample_user_id: UUID,
    sample_verification_code: VerificationCode,
) -> None:
    """verify_code should return the code when valid and unused."""
    mock_repository.get_unused_code_for_user.return_value = sample_verification_code

    result = await verification_service.verify_code(sample_user_id, 123456)

    assert result is sample_verification_code
    mock_repository.get_unused_code_for_user.assert_called_once_with(sample_user_id, 123456)


@pytest.mark.asyncio
async def test_verify_code_not_found(
    verification_service: VerificationService,
    mock_repository: AsyncMock,
    sample_user_id: UUID,
) -> None:
    """verify_code should raise error when code doesn't exist or is used."""
    mock_repository.get_unused_code_for_user.return_value = None

    with pytest.raises(VerificationCodeNotFoundError) as exc_info:
        await verification_service.verify_code(sample_user_id, 123456)

    assert "Invalid or used verification code: 123456" in str(exc_info.value)
    mock_repository.get_unused_code_for_user.assert_called_once_with(sample_user_id, 123456)


@pytest.mark.asyncio
async def test_verify_code_expired(
    verification_service: VerificationService,
    mock_repository: AsyncMock,
    sample_user_id: UUID,
    expired_verification_code: VerificationCode,
) -> None:
    """verify_code should raise error when code is expired."""
    mock_repository.get_unused_code_for_user.return_value = expired_verification_code

    with pytest.raises(VerificationCodeExpiredError) as exc_info:
        await verification_service.verify_code(sample_user_id, 654321)

    assert "Verification code has expired: 654321" in str(exc_info.value)
    mock_repository.get_unused_code_for_user.assert_called_once_with(sample_user_id, 654321)


def test_is_code_expired_true(
    verification_service: VerificationService,
    expired_verification_code: VerificationCode,
) -> None:
    """is_code_expired should return True for expired codes."""
    result = verification_service.is_code_expired(expired_verification_code)
    assert result is True


def test_is_code_expired_false(
    verification_service: VerificationService,
    sample_verification_code: VerificationCode,
) -> None:
    """is_code_expired should return False for valid codes."""
    result = verification_service.is_code_expired(sample_verification_code)
    assert result is False


@pytest.mark.asyncio
async def test_mark_code_as_used_success(
    verification_service: VerificationService,
    mock_repository: AsyncMock,
    sample_verification_code: VerificationCode,
) -> None:
    """mark_code_as_used should mark the code as used and return it."""
    # Ensure initial state is unused
    assert sample_verification_code.is_used is False

    updated_code = MagicMock()
    updated_code.id = sample_verification_code.id
    mock_repository.mark_as_used.return_value = updated_code

    result = await verification_service.mark_code_as_used(sample_verification_code)

    assert result is updated_code
    mock_repository.mark_as_used.assert_called_once_with(sample_verification_code)


@pytest.mark.asyncio
async def test_mark_code_as_used_already_used(
    verification_service: VerificationService,
    mock_repository: AsyncMock,
    used_verification_code: VerificationCode,
) -> None:
    """mark_code_as_used should handle already used codes gracefully."""
    # Ensure initial state is used
    assert used_verification_code.is_used is True

    # The service should return the code directly without calling repository
    result = await verification_service.mark_code_as_used(used_verification_code)

    assert result is used_verification_code
    assert result.is_used is True
    mock_repository.mark_as_used.assert_not_called()


@pytest.mark.asyncio
async def test_verify_and_consume_code_success(
    verification_service: VerificationService,
    mock_repository: AsyncMock,
    sample_user_id: UUID,
    sample_verification_code: VerificationCode,
) -> None:
    """verify_and_consume_code should verify and mark code as used."""
    # Mock the repository methods
    mock_repository.get_unused_code_for_user.return_value = sample_verification_code

    # Mock mark_as_used to return the updated code
    consumed_code = MagicMock()
    consumed_code.id = sample_verification_code.id
    mock_repository.mark_as_used.return_value = consumed_code

    result = await verification_service.verify_and_consume_code(sample_user_id, 123456)

    assert result is consumed_code
    mock_repository.get_unused_code_for_user.assert_called_once_with(sample_user_id, 123456)
    mock_repository.mark_as_used.assert_called_once_with(sample_verification_code)


@pytest.mark.asyncio
async def test_verify_and_consume_code_expired(
    verification_service: VerificationService,
    mock_repository: AsyncMock,
    sample_user_id: UUID,
    expired_verification_code: VerificationCode,
) -> None:
    """verify_and_consume_code should raise error when code is expired."""
    mock_repository.get_unused_code_for_user.return_value = expired_verification_code

    with pytest.raises(VerificationCodeExpiredError):
        await verification_service.verify_and_consume_code(sample_user_id, 654321)

    mock_repository.get_unused_code_for_user.assert_called_once_with(sample_user_id, 654321)
    mock_repository.mark_as_used.assert_not_called()


@pytest.mark.asyncio
async def test_verify_and_consume_code_not_found(
    verification_service: VerificationService,
    mock_repository: AsyncMock,
    sample_user_id: UUID,
) -> None:
    """verify_and_consume_code should raise error when code doesn't exist."""
    mock_repository.get_unused_code_for_user.return_value = None

    with pytest.raises(VerificationCodeNotFoundError):
        await verification_service.verify_and_consume_code(sample_user_id, 999999)

    mock_repository.get_unused_code_for_user.assert_called_once_with(sample_user_id, 999999)
    mock_repository.mark_as_used.assert_not_called()


# Test edge cases
@pytest.mark.asyncio
async def test_generate_verification_code_minimum_boundary(
    verification_service: VerificationService,
    mock_repository: AsyncMock,
    sample_user_id: UUID,
) -> None:
    """generate_verification_code should generate codes within valid range."""
    # Mock to ensure uniqueness check passes
    mock_repository.get_by_code.return_value = None
    created_code = MagicMock()
    mock_repository.create.return_value = created_code

    # Generate multiple codes to test boundary conditions
    for _ in range(100):  # Test multiple generations
        await verification_service.generate_verification_code(sample_user_id)

        # Get the created code from the mock call
        call_args = mock_repository.create.call_args[0][0]
        generated_code = call_args.code

        assert 100000 <= generated_code <= 999999
        assert len(str(generated_code)) == 6


@pytest.mark.asyncio
async def test_is_code_expired_boundary_time(
    verification_service: VerificationService,
    sample_user_id: UUID,
) -> None:
    """is_code_expired should handle boundary time conditions correctly."""
    # Test code that expires exactly now
    now = datetime.now(UTC)
    boundary_code = VerificationCode(
        id=uuid4(),
        code=999999,
        expires_at=now,  # Expires exactly now
        is_used=False,
        local_user_id=sample_user_id,
    )

    # Should be considered expired (expires_at < now)
    result = verification_service.is_code_expired(boundary_code)
    assert result is True

    # Test code that expires 1 second in the future
    future_code = VerificationCode(
        id=uuid4(),
        code=888888,
        expires_at=now + timedelta(seconds=1),
        is_used=False,
        local_user_id=sample_user_id,
    )

    result = verification_service.is_code_expired(future_code)
    assert result is False


# TODO: add unit tests for logger side effects in all methods once they matter.
# TODO: add unit tests for integration scenarios and error propagation.
