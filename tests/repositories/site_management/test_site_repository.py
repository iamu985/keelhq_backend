"""Tests for SiteRepository.

Responsibility:
- Verify all read and write operations on SiteRepository using a mocked
  AsyncSession so the suite stays fast and isolated from the database.
"""

from collections.abc import Sequence
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Site
from app.repositories.site_management.site_repository import SiteRepository
from app.schemas.site_management.site_schemas import ListSiteQuery
from app.shared.enums import SiteStatus


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
def sample_site() -> Site:
    """Return a deterministic Site instance for assertions."""
    return Site(
        id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        owner_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        name="My Site",
        slug="my-site",
        status="active",
        visibility="public",
    )


@pytest.fixture
def repository(mock_session: AsyncMock) -> SiteRepository:
    """Return a SiteRepository backed by the mocked session."""
    return SiteRepository(session=cast(AsyncSession, mock_session))


# TODO: add unit tests for logging assertions once they matter.
async def test_get_site_by_id_found(
    repository: SiteRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_site: Site,
) -> None:
    """get(site_id) should return the site when the query matches."""
    mock_result.scalar_one_or_none.return_value = sample_site
    mock_session.execute.return_value = mock_result

    site = await repository.get(sample_site.id)

    assert site is sample_site
    mock_session.execute.assert_awaited_once()


async def test_get_site_by_id_not_found(
    repository: SiteRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get(site_id) should return None when no site matches."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    site = await repository.get(uuid4())

    assert site is None
    mock_session.execute.assert_awaited_once()


async def test_get_by_slug_found(
    repository: SiteRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_site: Site,
) -> None:
    """get_by_slug(slug) should return the site with a matching slug."""
    mock_result.scalar_one_or_none.return_value = sample_site
    mock_session.execute.return_value = mock_result

    site = await repository.get_by_slug("my-site")

    assert site is sample_site
    mock_session.execute.assert_awaited_once()


async def test_get_by_slug_not_found(
    repository: SiteRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get_by_slug(slug) should return None when the slug is unknown."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    site = await repository.get_by_slug("nonexistent")

    assert site is None
    mock_session.execute.assert_awaited_once()


async def test_get_by_owner(
    repository: SiteRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_site: Site,
) -> None:
    """get_by_owner(owner_id) should return all sites for that owner."""
    mock_result.scalars.return_value.all.return_value = [sample_site]
    mock_session.execute.return_value = mock_result

    sites: Sequence[Site] = await repository.get_by_owner(sample_site.owner_id)

    assert sites == [sample_site]
    mock_session.execute.assert_awaited_once()


async def test_get_by_owner_empty(
    repository: SiteRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get_by_owner(owner_id) should return empty sequence when no sites exist."""
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    sites = await repository.get_by_owner(uuid4())

    assert sites == []
    mock_session.execute.assert_awaited_once()


async def test_create_site(
    repository: SiteRepository,
    mock_session: AsyncMock,
    sample_site: Site,
) -> None:
    """create(site) should add, flush, refresh, and return the site."""
    created = await repository.create(sample_site)

    assert created is sample_site
    mock_session.add.assert_called_once_with(sample_site)
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(sample_site)


async def test_list_sites_no_query(
    repository: SiteRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_site: Site,
) -> None:
    """list(None) should return all sites without any filter."""
    mock_result.scalars.return_value.all.return_value = [sample_site]
    mock_session.execute.return_value = mock_result

    sites = await repository.list()

    assert sites == [sample_site]
    mock_session.execute.assert_awaited_once()


async def test_list_sites_with_status_filter(
    repository: SiteRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_site: Site,
) -> None:
    """list(query) should apply status filter when provided."""
    mock_result.scalars.return_value.all.return_value = [sample_site]
    mock_session.execute.return_value = mock_result

    query = ListSiteQuery(status=SiteStatus.ACTIVE)
    sites = await repository.list(query=query)

    assert sites == [sample_site]
    mock_session.execute.assert_awaited_once()


async def test_list_sites_with_owner_filter(
    repository: SiteRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_site: Site,
) -> None:
    """list(query) should apply owner_id filter when provided."""
    mock_result.scalars.return_value.all.return_value = [sample_site]
    mock_session.execute.return_value = mock_result

    query = ListSiteQuery(owner_id=sample_site.owner_id)
    sites = await repository.list(query=query)

    assert sites == [sample_site]
    mock_session.execute.assert_awaited_once()


async def test_list_sites_empty(
    repository: SiteRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """list() should return an empty sequence when no sites exist."""
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    sites = await repository.list()

    assert sites == []
    mock_session.execute.assert_awaited_once()


async def test_delete_site(
    repository: SiteRepository,
    mock_session: AsyncMock,
    sample_site: Site,
) -> None:
    """delete(site) should delete the site, flush, and return it."""
    deleted = await repository.delete(sample_site)

    assert deleted is sample_site
    mock_session.delete.assert_awaited_once_with(sample_site)
    mock_session.flush.assert_awaited_once()
