"""Media asset repository.

Responsibility:
- Provide all database read and write operations for the MediaAsset model.
- Remain free of business logic and exception handling.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from keelhq.core.logger import logger
from keelhq.db.models import MediaAsset


# TODO: add unit tests for this repository
class MediaAssetRepository:
    """Data access layer for the MediaAsset model.

    Responsibility:
    - Execute parameterised SQL queries against the media_assets table.
    - Return domain model instances or sequences; never raw rows or dicts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, asset_id: UUID) -> MediaAsset | None:
        """Return the asset with the given primary key, or None if not found."""
        logger.info("Fetching MediaAsset by id.")
        logger.debug(f"asset_id={asset_id}")

        stmt = select(MediaAsset).where(MediaAsset.id == asset_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_storage_key(self, storage_key: str) -> MediaAsset | None:
        """Return the asset with the given unique storage key, or None if not found.

        The storage_key is the opaque provider-specific identifier returned after
        uploading a file to the external storage service.
        """
        logger.info("Fetching MediaAsset by storage_key.")
        logger.debug(f"storage_key={storage_key}")

        stmt = select(MediaAsset).where(MediaAsset.storage_key == storage_key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_site(
        self,
        site_id: UUID,
        mime_type: str | None = None,
        extension: str | None = None,
    ) -> Sequence[MediaAsset]:
        """Return all assets for a site, with optional mime_type and extension filters."""
        logger.info("Listing MediaAssets by site_id.")
        logger.debug(f"site_id={site_id} mime_type={mime_type} extension={extension}")

        stmt = select(MediaAsset).where(MediaAsset.site_id == site_id)
        if mime_type is not None:
            stmt = stmt.where(MediaAsset.mime_type == mime_type)
        if extension is not None:
            stmt = stmt.where(MediaAsset.extension == extension)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, asset: MediaAsset) -> MediaAsset:
        """Persist a new MediaAsset and return the refreshed instance."""
        logger.info("Creating MediaAsset.")
        logger.debug(f"site_id={asset.site_id} storage_key={asset.storage_key}")

        self.session.add(asset)
        await self.session.flush()
        await self.session.refresh(asset)
        return asset

    async def delete(self, asset: MediaAsset) -> MediaAsset:
        """Delete the given MediaAsset and return the deleted instance."""
        logger.info("Deleting MediaAsset.")
        logger.debug(f"asset_id={asset.id}")

        await self.session.delete(asset)
        await self.session.flush()
        return asset
