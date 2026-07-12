"""Tests for ContentEntryRepository.

Responsibility:
- Verify all read and write operations on ContentEntryRepository using a mocked
  AsyncSession so the suite stays fast and isolated from the database.
"""

from collections.abc import Sequence
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from keelhq.db.models import ContentEntry
from keelhq.repositories.content_engine.content_entry_repository import (
    ContentEntryRepository,
)
from keelhq.shared.enums import ContentStatus

SITE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
DEFINITION_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


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
def sample_entry() -> ContentEntry:
    """Return a deterministic ContentEntry instance for assertions."""
    return ContentEntry(
        id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        site_id=SITE_ID,
        definition_id=DEFINITION_ID,
        slug="hero",
        status=ContentStatus.DRAFT,
        sort_order=0,
        content={},
    )


@pytest.fixture
def repository(mock_session: AsyncMock) -> ContentEntryRepository:
    """Return a ContentEntryRepository backed by the mocked session."""
    return ContentEntryRepository(session=cast(AsyncSession, mock_session))


# TODO: add unit tests for logging assertions once they matter.
async def test_get_entry_by_id_found(
    repository: ContentEntryRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_entry: ContentEntry,
) -> None:
    """get(entry_id) should return the entry when the query matches."""
    mock_result.scalar_one_or_none.return_value = sample_entry
    mock_session.execute.return_value = mock_result

    entry = await repository.get(sample_entry.id)

    assert entry is sample_entry
    mock_session.execute.assert_awaited_once()


async def test_get_entry_by_id_not_found(
    repository: ContentEntryRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get(entry_id) should return None when no entry matches."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    entry = await repository.get(uuid4())

    assert entry is None
    mock_session.execute.assert_awaited_once()


async def test_get_by_site_and_slug_found(
    repository: ContentEntryRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_entry: ContentEntry,
) -> None:
    """get_by_site_and_slug should return the entry with the matching slug within that site."""
    mock_result.scalar_one_or_none.return_value = sample_entry
    mock_session.execute.return_value = mock_result

    entry = await repository.get_by_site_and_slug(SITE_ID, "hero")

    assert entry is sample_entry
    mock_session.execute.assert_awaited_once()


async def test_get_by_site_and_slug_not_found(
    repository: ContentEntryRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get_by_site_and_slug should return None when the slug is unknown for that site."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    entry = await repository.get_by_site_and_slug(SITE_ID, "nonexistent")

    assert entry is None
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_no_filters(
    repository: ContentEntryRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_entry: ContentEntry,
) -> None:
    """list_by_site without filters should return all entries for that site."""
    mock_result.scalars.return_value.all.return_value = [sample_entry]
    mock_session.execute.return_value = mock_result

    entries: Sequence[ContentEntry] = await repository.list_by_site(SITE_ID)

    assert entries == [sample_entry]
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_with_status_filter(
    repository: ContentEntryRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_entry: ContentEntry,
) -> None:
    """list_by_site with status filter should return only matching entries."""
    mock_result.scalars.return_value.all.return_value = [sample_entry]
    mock_session.execute.return_value = mock_result

    entries = await repository.list_by_site(SITE_ID, status=ContentStatus.DRAFT)

    assert entries == [sample_entry]
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_with_definition_filter(
    repository: ContentEntryRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_entry: ContentEntry,
) -> None:
    """list_by_site with definition_id filter should narrow results."""
    mock_result.scalars.return_value.all.return_value = [sample_entry]
    mock_session.execute.return_value = mock_result

    entries = await repository.list_by_site(SITE_ID, definition_id=DEFINITION_ID)

    assert entries == [sample_entry]
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_empty(
    repository: ContentEntryRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """list_by_site should return empty sequence when no entries exist."""
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    entries = await repository.list_by_site(uuid4())

    assert entries == []
    mock_session.execute.assert_awaited_once()


async def test_list_by_definition_no_filter(
    repository: ContentEntryRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_entry: ContentEntry,
) -> None:
    """list_by_definition without status filter should return all entries for that definition."""
    mock_result.scalars.return_value.all.return_value = [sample_entry]
    mock_session.execute.return_value = mock_result

    entries = await repository.list_by_definition(DEFINITION_ID)

    assert entries == [sample_entry]
    mock_session.execute.assert_awaited_once()


async def test_list_by_definition_with_status(
    repository: ContentEntryRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_entry: ContentEntry,
) -> None:
    """list_by_definition with status filter should narrow results."""
    mock_result.scalars.return_value.all.return_value = [sample_entry]
    mock_session.execute.return_value = mock_result

    entries = await repository.list_by_definition(DEFINITION_ID, status=ContentStatus.PUBLISHED)

    assert entries == [sample_entry]
    mock_session.execute.assert_awaited_once()


async def test_create_entry(
    repository: ContentEntryRepository,
    mock_session: AsyncMock,
    sample_entry: ContentEntry,
) -> None:
    """create(entry) should add, flush, refresh, and return the entry."""
    created = await repository.create(sample_entry)

    assert created is sample_entry
    mock_session.add.assert_called_once_with(sample_entry)
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(sample_entry)


async def test_delete_entry(
    repository: ContentEntryRepository,
    mock_session: AsyncMock,
    sample_entry: ContentEntry,
) -> None:
    """delete(entry) should delete the entry, flush, and return it."""
    deleted = await repository.delete(sample_entry)

    assert deleted is sample_entry
    mock_session.delete.assert_awaited_once_with(sample_entry)
    mock_session.flush.assert_awaited_once()
