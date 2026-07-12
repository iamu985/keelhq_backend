"""Tests for LocalUserRepository.

Responsibility:
- Verify all read and write operations on LocalUserRepository using a mocked
  AsyncSession so the suite stays fast and isolated from the database.
"""

from collections.abc import Sequence
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LocalUser
from app.repositories.identity.local_user_repository import LocalUserRepository


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
def sample_user() -> LocalUser:
    """Return a deterministic LocalUser instance for assertions."""
    return LocalUser(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        email="alice@example.com",
        username="alice",
        password_hash="hashed-secret",
        first_name="Alice",
        middle_name=None,
        last_name="Smith",
        is_active=True,
        is_superuser=False,
    )


@pytest.fixture
def repository(mock_session: AsyncMock) -> LocalUserRepository:
    """Return a LocalUserRepository backed by the mocked session."""
    return LocalUserRepository(session=cast(AsyncSession, mock_session))


# TODO: add unit tests for the logger side effects in get() once they matter.
@pytest.mark.asyncio
async def test_get_user_by_id_found(
    repository: LocalUserRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_user: LocalUser,
) -> None:
    """get(user_id) should return the user when the query matches."""
    mock_result.scalar_one_or_none.return_value = sample_user
    mock_session.execute.return_value = mock_result

    user = await repository.get(sample_user.id)

    assert user is sample_user
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(
    repository: LocalUserRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get(user_id) should return None when no user matches."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    user = await repository.get(uuid4())

    assert user is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_email_found(
    repository: LocalUserRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_user: LocalUser,
) -> None:
    """get_by_email(email) should return the user with a matching email."""
    mock_result.scalar_one_or_none.return_value = sample_user
    mock_session.execute.return_value = mock_result

    user = await repository.get_by_email(sample_user.email)

    assert user is sample_user
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_email_not_found(
    repository: LocalUserRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get_by_email(email) should return None when the email is unknown."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    user = await repository.get_by_email("missing@example.com")

    assert user is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_username_found(
    repository: LocalUserRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_user: LocalUser,
) -> None:
    """get_by_username(username) should return the user with a matching username."""
    mock_result.scalar_one_or_none.return_value = sample_user
    mock_session.execute.return_value = mock_result

    user = await repository.get_by_username(sample_user.username)

    assert user is sample_user
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_username_not_found(
    repository: LocalUserRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get_by_username(username) should return None when the username is unknown."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    user = await repository.get_by_username("nobody")

    assert user is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_user(
    repository: LocalUserRepository,
    mock_session: AsyncMock,
    sample_user: LocalUser,
) -> None:
    """create(user) should add, flush, refresh, and return the user."""
    created_user = await repository.create(sample_user)

    assert created_user is sample_user
    mock_session.add.assert_called_once_with(sample_user)
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(sample_user)


@pytest.mark.asyncio
async def test_list_users(
    repository: LocalUserRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_user: LocalUser,
) -> None:
    """list() should return all users returned by the scalar result."""
    mock_result.scalars.return_value.all.return_value = [sample_user]
    mock_session.execute.return_value = mock_result

    users: Sequence[LocalUser] = await repository.list()

    assert users == [sample_user]
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_users_empty(
    repository: LocalUserRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """list() should return an empty sequence when no users exist."""
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    users = await repository.list()

    assert users == []
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_user(
    repository: LocalUserRepository,
    mock_session: AsyncMock,
    sample_user: LocalUser,
) -> None:
    """delete(user) should delete the user and flush the session."""
    deleted_user = await repository.delete(sample_user)

    assert deleted_user is sample_user
    mock_session.delete.assert_awaited_once_with(sample_user)
    mock_session.flush.assert_awaited_once()
