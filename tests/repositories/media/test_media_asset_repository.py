"""Tests for MediaAssetRepository.

Responsibility:
- Verify all read and write operations on MediaAssetRepository using a mocked
  AsyncSession so the suite stays fast and isolated from the database.
"""

from collections.abc import Sequence
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from keelhq.db.models import MediaAsset
from keelhq.repositories.media.media_asset_repository import MediaAssetRepository

SITE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
STORAGE_KEY = "uploads/2024/hero.jpg"


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
def sample_asset() -> MediaAsset:
    """Return a deterministic MediaAsset instance for assertions."""
    return MediaAsset(
        id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        site_id=SITE_ID,
        filename="hero.jpg",
        storage_key=STORAGE_KEY,
        mime_type="image/jpeg",
        extension="jpg",
        size=204800,
        extra_metadata={},
    )


@pytest.fixture
def repository(mock_session: AsyncMock) -> MediaAssetRepository:
    """Return a MediaAssetRepository backed by the mocked session."""
    return MediaAssetRepository(session=cast(AsyncSession, mock_session))


# TODO: add unit tests for logging assertions once they matter.
async def test_get_asset_by_id_found(
    repository: MediaAssetRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_asset: MediaAsset,
) -> None:
    """get(asset_id) should return the asset when the query matches."""
    mock_result.scalar_one_or_none.return_value = sample_asset
    mock_session.execute.return_value = mock_result

    asset = await repository.get(sample_asset.id)

    assert asset is sample_asset
    mock_session.execute.assert_awaited_once()


async def test_get_asset_by_id_not_found(
    repository: MediaAssetRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get(asset_id) should return None when no asset matches."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    asset = await repository.get(uuid4())

    assert asset is None
    mock_session.execute.assert_awaited_once()


async def test_get_by_storage_key_found(
    repository: MediaAssetRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_asset: MediaAsset,
) -> None:
    """get_by_storage_key should return the asset with the matching storage key."""
    mock_result.scalar_one_or_none.return_value = sample_asset
    mock_session.execute.return_value = mock_result

    asset = await repository.get_by_storage_key(STORAGE_KEY)

    assert asset is sample_asset
    mock_session.execute.assert_awaited_once()


async def test_get_by_storage_key_not_found(
    repository: MediaAssetRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """get_by_storage_key should return None when the key is unknown."""
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    asset = await repository.get_by_storage_key("nonexistent/key.png")

    assert asset is None
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_no_filter(
    repository: MediaAssetRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_asset: MediaAsset,
) -> None:
    """list_by_site without filters should return all assets for that site."""
    mock_result.scalars.return_value.all.return_value = [sample_asset]
    mock_session.execute.return_value = mock_result

    assets: Sequence[MediaAsset] = await repository.list_by_site(SITE_ID)

    assert assets == [sample_asset]
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_mime_type_filter(
    repository: MediaAssetRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_asset: MediaAsset,
) -> None:
    """list_by_site with mime_type filter should narrow results."""
    mock_result.scalars.return_value.all.return_value = [sample_asset]
    mock_session.execute.return_value = mock_result

    assets = await repository.list_by_site(SITE_ID, mime_type="image/jpeg")

    assert assets == [sample_asset]
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_extension_filter(
    repository: MediaAssetRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
    sample_asset: MediaAsset,
) -> None:
    """list_by_site with extension filter should narrow results."""
    mock_result.scalars.return_value.all.return_value = [sample_asset]
    mock_session.execute.return_value = mock_result

    assets = await repository.list_by_site(SITE_ID, extension="jpg")

    assert assets == [sample_asset]
    mock_session.execute.assert_awaited_once()


async def test_list_by_site_empty(
    repository: MediaAssetRepository,
    mock_session: AsyncMock,
    mock_result: MagicMock,
) -> None:
    """list_by_site should return empty sequence when no assets exist for the site."""
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    assets = await repository.list_by_site(uuid4())

    assert assets == []
    mock_session.execute.assert_awaited_once()


async def test_create_asset(
    repository: MediaAssetRepository,
    mock_session: AsyncMock,
    sample_asset: MediaAsset,
) -> None:
    """create(asset) should add, flush, refresh, and return the asset."""
    created = await repository.create(sample_asset)

    assert created is sample_asset
    mock_session.add.assert_called_once_with(sample_asset)
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(sample_asset)


async def test_delete_asset(
    repository: MediaAssetRepository,
    mock_session: AsyncMock,
    sample_asset: MediaAsset,
) -> None:
    """delete(asset) should delete the asset, flush, and return it."""
    deleted = await repository.delete(sample_asset)

    assert deleted is sample_asset
    mock_session.delete.assert_awaited_once_with(sample_asset)
    mock_session.flush.assert_awaited_once()
