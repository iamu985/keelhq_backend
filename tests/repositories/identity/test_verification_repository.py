"""Tests for VerificationCodeRepository.

Responsibility:
- Verify all read and write operations on VerificationCodeRepository using a mocked
  AsyncSession so the suite stays fast and isolated from the database.
"""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from keelhq.db.models import VerificationCode
from keelhq.repositories.identity.verification_repository import VerificationCodeRepository


@pytest.fixture
def mock_session() -> AsyncMock:
    """Return a mocked AsyncSession with async methods pre-wired.

    The repository awaits session.execute/flush/refresh/delete, so those
    methods are AsyncMock instances. Result objects are synchronous mocks.
    """
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def mock_result() -> MagicMock:
    """Return a MagicMock that mimics SQLAlchemy's Result object.

    Provides both scalar_one_or_none() and scalars().all() patterns used by
    the repository methods.
    """
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=None)

    scalar_result = MagicMock()
    scalar_result.all = MagicMock(return_value=[])
    result.scalars = MagicMock(return_value=scalar_result)

    return result


@pytest.fixture
def sample_verification_code() -> VerificationCode:
    """Return a deterministic VerificationCode instance for assertions."""
    return VerificationCode(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        code=123456,
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
        is_used=False,
        local_user_id=UUID("87654321-4321-8765-4321-876543210987"),
    )


@pytest.fixture
def repository(mock_session: AsyncMock) -> VerificationCodeRepository:
    """Return a VerificationCodeRepository backed by the mocked session."""
    return VerificationCodeRepository(session=cast(AsyncSession, mock_session))


@pytest.mark.asyncio
async def test_get_verification_code_by_id_found(
    repository: VerificationCodeRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_verification_code: VerificationCode,
) -> None:
    """get(id_) should return the verification code when the query matches."""
    mock_result.scalar_one_or_none.return_value = sample_verification_code
    mock_session.execute.return_value = mock_result

    code = await repository.get(sample_verification_code.id)

    assert code is sample_verification_code
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_verification_code_by_id_not_found(
    repository: VerificationCodeRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get(id_) should return None when no verification code matches."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    code = await repository.get(uuid4())

    assert code is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_verification_code_by_code_found(
    repository: VerificationCodeRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_verification_code: VerificationCode,
) -> None:
    """get_by_code(code) should return the verification code with a matching code."""
    mock_result.scalar_one_or_none.return_value = sample_verification_code
    mock_session.execute.return_value = mock_result

    code = await repository.get_by_code(sample_verification_code.code)

    assert code is sample_verification_code
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_verification_code_by_code_not_found(
    repository: VerificationCodeRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get_by_code(code) should return None when the code is unknown."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    code = await repository.get_by_code(999999)

    assert code is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_unused_code_for_user_found(
    repository: VerificationCodeRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_verification_code: VerificationCode,
) -> None:
    """get_unused_code_for_user should return unused code for the user."""
    mock_result.scalar_one_or_none.return_value = sample_verification_code
    mock_session.execute.return_value = mock_result

    code = await repository.get_unused_code_for_user(
        sample_verification_code.local_user_id, sample_verification_code.code
    )

    assert code is sample_verification_code
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_unused_code_for_user_not_found(
    repository: VerificationCodeRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get_unused_code_for_user should return None when no unused code matches."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    code = await repository.get_unused_code_for_user(uuid4(), 123456)

    assert code is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_verification_code(
    repository: VerificationCodeRepository,
    mock_session: AsyncMock,
    sample_verification_code: VerificationCode,
) -> None:
    """create(verification_code) should add, flush, refresh, and return the code."""
    created_code = await repository.create(sample_verification_code)

    assert created_code is sample_verification_code
    mock_session.add.assert_called_once_with(sample_verification_code)
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(sample_verification_code)


@pytest.mark.asyncio
async def test_mark_as_used(
    repository: VerificationCodeRepository,
    mock_session: AsyncMock,
    sample_verification_code: VerificationCode,
) -> None:
    """mark_as_used should update is_used to True and return the code."""
    # Ensure initial state is unused
    assert sample_verification_code.is_used is False

    updated_code = await repository.mark_as_used(sample_verification_code)

    assert updated_code is sample_verification_code
    assert sample_verification_code.is_used is True
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(sample_verification_code)


@pytest.mark.asyncio
async def test_mark_as_used_already_used(
    repository: VerificationCodeRepository,
    mock_session: AsyncMock,
    sample_verification_code: VerificationCode,
) -> None:
    """mark_as_used should handle already used codes gracefully."""
    # Set initial state to used
    sample_verification_code.is_used = True

    updated_code = await repository.mark_as_used(sample_verification_code)

    assert updated_code is sample_verification_code
    assert sample_verification_code.is_used is True
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(sample_verification_code)


@pytest.mark.asyncio
async def test_list_verification_codes(
    repository: VerificationCodeRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_verification_code: VerificationCode,
) -> None:
    """list() should return all verification codes returned by the scalar result."""
    mock_result.scalars.return_value.all.return_value = [sample_verification_code]
    mock_session.execute.return_value = mock_result

    codes: Sequence[VerificationCode] = await repository.list()

    assert codes == [sample_verification_code]
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_verification_codes_empty(
    repository: VerificationCodeRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """list() should return an empty sequence when no verification codes exist."""
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    codes = await repository.list()

    assert codes == []
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_verification_code(
    repository: VerificationCodeRepository,
    mock_session: AsyncMock,
    sample_verification_code: VerificationCode,
) -> None:
    """delete(verification_code) should delete the code and flush the session."""
    deleted_code = await repository.delete(sample_verification_code)

    assert deleted_code is sample_verification_code
    mock_session.delete.assert_awaited_once_with(sample_verification_code)
    mock_session.flush.assert_awaited_once()


# TODO: add unit tests for the logger side effects in all methods once they matter.
# TODO: add unit tests for database transaction handling and error scenarios.
