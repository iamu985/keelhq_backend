"""Content entry repository.

Responsibility:
- Provide all database read and write operations for the ContentEntry model.
- Remain free of business logic and exception handling.
"""

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.logger import logger
from app.db.models import ContentEntry
from app.shared.enums import ContentStatus


# TODO: add unit tests for this repository
class ContentEntryRepository:
    """Data access layer for the ContentEntry model.

    Responsibility:
    - Execute parameterised SQL queries against the content_entries table.
    - Return domain model instances or sequences; never raw rows or dicts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, entry_id: UUID) -> Optional[ContentEntry]:
        """Return the content entry with the given primary key, or None if not found."""
        logger.info("Fetching ContentEntry by id.")
        logger.debug(f"entry_id={entry_id}")

        stmt = select(ContentEntry).where(ContentEntry.id == entry_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_site_and_slug(
        self, site_id: UUID, slug: str
    ) -> Optional[ContentEntry]:
        """Return the entry within a site that matches the given slug, or None.

        Slug uniqueness is scoped per site, so both site_id and slug are required.
        """
        logger.info("Fetching ContentEntry by site_id and slug.")
        logger.debug(f"site_id={site_id} slug={slug}")

        stmt = select(ContentEntry).where(
            ContentEntry.site_id == site_id,
            ContentEntry.slug == slug,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_site(
        self,
        site_id: UUID,
        status: Optional[ContentStatus] = None,
        definition_id: Optional[UUID] = None,
    ) -> Sequence[ContentEntry]:
        """Return all entries for a site, with optional status and definition filters."""
        logger.info("Listing ContentEntries by site_id.")
        logger.debug(f"site_id={site_id} status={status} definition_id={definition_id}")

        stmt = select(ContentEntry).where(ContentEntry.site_id == site_id)
        if status is not None:
            stmt = stmt.where(ContentEntry.status == status)
        if definition_id is not None:
            stmt = stmt.where(ContentEntry.definition_id == definition_id)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_definition(
        self,
        definition_id: UUID,
        status: Optional[ContentStatus] = None,
    ) -> Sequence[ContentEntry]:
        """Return all entries for a specific definition, with optional status filter."""
        logger.info("Listing ContentEntries by definition_id.")
        logger.debug(f"definition_id={definition_id} status={status}")

        stmt = select(ContentEntry).where(ContentEntry.definition_id == definition_id)
        if status is not None:
            stmt = stmt.where(ContentEntry.status == status)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, entry: ContentEntry) -> ContentEntry:
        """Persist a new ContentEntry and return the refreshed instance."""
        logger.info("Creating ContentEntry.")
        logger.debug(f"site_id={entry.site_id} definition_id={entry.definition_id}")

        self.session.add(entry)
        await self.session.flush()
        await self.session.refresh(entry)
        return entry

    async def delete(self, entry: ContentEntry) -> ContentEntry:
        """Delete the given ContentEntry and return the deleted instance."""
        logger.info("Deleting ContentEntry.")
        logger.debug(f"entry_id={entry.id}")

        await self.session.delete(entry)
        await self.session.flush()
        return entry
