"""Tests for AccessTokenRepository.

Responsibility:
- Verify all read and write operations on AccessTokenRepository using a mocked
  AsyncSession so the suite stays fast and isolated from the database.
"""

from collections.abc import Sequence
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from keelhq.db.models import AccessToken
from keelhq.repositories.integration.access_token_repository import AccessTokenRepository

SITE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
TOKEN_HASH = "sha256-abc123"


@pytest.fixture
def mock_session() -> AsyncMock:
    """Return a mocked AsyncSession with all async methods pre-wired."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def mock_result() -> MagicMock:
    """Return a MagicMock that mimics SQLAlchemy's Result object."""
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=None)
    scalar_result = MagicMock()
    scalar_result.all = MagicMock(return_value=[])
    result.scalars = MagicMock(return_value=scalar_result)
    return result


@pytest.fixture
def sample_token() -> AccessToken:
    """Return a deterministic AccessToken instance for assertions."""
    return AccessToken(
        id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        site_id=SITE_ID,
        name="Claude Code",
        token_hash=TOKEN_HASH,
        is_active=True,
    )


@pytest.fixture
def repository(mock_session: AsyncMock) -> AccessTokenRepository:
    """Return an AccessTokenRepository backed by the mocked session."""
    return AccessTokenRepository(session=cast(AsyncSession, mock_session))


# TODO: add unit tests for logging assertions once they matter.
async def test_get_token_by_id_found(
    repository: AccessTokenRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_token: AccessToken,
) -> None:
    """get(token_id) should return the token when the query matches."""
    mock_result.scalar_one_or_none.return_value = sample_token
    mock_session.execute.return_value = mock_result

    token = await repository.get(sample_token.id)

    assert token is sample_token
    mock_session.execute.assert_awaited_once()


async def test_get_token_by_id_not_found(
    repository: AccessTokenRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get(token_id) should return None when no token matches."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    token = await repository.get(uuid4())

    assert token is None
    mock_session.execute.assert_awaited_once()


async def test_get_by_token_hash_found(
    repository: AccessTokenRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_token: AccessToken,
) -> None:
    """get_by_token_hash should return the token with the matching hash."""
    mock_result.scalar_one_or_none.return_value = sample_token
    mock_session.execute.return_value = mock_result

    token = await repository.get_by_token_hash(TOKEN_HASH)

    assert token is sample_token
    mock_session.execute.assert_awaited_once()


async def test_get_by_token_hash_not_found(
    repository: AccessTokenRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get_by_token_hash should return None when the hash is unknown."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    token = await repository.get_by_token_hash("nonexistent-hash")

    assert token is None
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_no_filter(
    repository: AccessTokenRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_token: AccessToken,
) -> None:
    """list_by_site without is_active filter should return all tokens for that site."""
    mock_result.scalars.return_value.all.return_value = [sample_token]
    mock_session.execute.return_value = mock_result

    tokens: Sequence[AccessToken] = await repository.list_by_site(SITE_ID)

    assert tokens == [sample_token]
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_active_only(
    repository: AccessTokenRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_token: AccessToken,
) -> None:
    """list_by_site with is_active=True should filter to active tokens only."""
    mock_result.scalars.return_value.all.return_value = [sample_token]
    mock_session.execute.return_value = mock_result

    tokens = await repository.list_by_site(SITE_ID, is_active=True)

    assert tokens == [sample_token]
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_inactive_only(
    repository: AccessTokenRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """list_by_site with is_active=False should return inactive tokens only."""
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    tokens = await repository.list_by_site(SITE_ID, is_active=False)

    assert tokens == []
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_empty(
    repository: AccessTokenRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """list_by_site should return empty sequence when no tokens exist for the site."""
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    tokens = await repository.list_by_site(uuid4())

    assert tokens == []
    mock_session.execute.assert_awaited_once()


async def test_create_token(
    repository: AccessTokenRepository,
    mock_session: AsyncMock,
    sample_token: AccessToken,
) -> None:
    """create(token) should add, flush, refresh, and return the token."""
    created = await repository.create(sample_token)

    assert created is sample_token
    mock_session.add.assert_called_once_with(sample_token)
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(sample_token)


async def test_delete_token(
    repository: AccessTokenRepository,
    mock_session: AsyncMock,
    sample_token: AccessToken,
) -> None:
    """delete(token) should delete the token, flush, and return it."""
    deleted = await repository.delete(sample_token)

    assert deleted is sample_token
    mock_session.delete.assert_awaited_once_with(sample_token)
    mock_session.flush.assert_awaited_once()
