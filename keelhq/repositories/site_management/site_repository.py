"""Site repository.

Responsibility:
- Provide all database read and write operations for the Site model.
- Remain free of business logic and exception handling.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from keelhq.core.logger import logger
from keelhq.db.models import Site
from keelhq.schemas.site_management.site_schemas import ListSiteQuery


# TODO: add unit tests for this repository
class SiteRepository:
    """Data access layer for the Site model.

    Responsibility:
    - Execute parameterised SQL queries against the sites table.
    - Return domain model instances or sequences; never raw rows or dicts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, site_id: UUID) -> Site | None:
        """Return the site with the given primary key, or None if not found."""
        logger.info("Fetching Site by id.")
        logger.debug(f"site_id={site_id}")

        stmt = select(Site).where(Site.id == site_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Site | None:
        """Return the site with the given unique slug, or None if not found."""
        logger.info("Fetching Site by slug.")
        logger.debug(f"slug={slug}")

        stmt = select(Site).where(Site.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: UUID) -> Sequence[Site]:
        """Return all sites belonging to the given owner."""
        logger.info("Fetching Sites by owner_id.")
        logger.debug(f"owner_id={owner_id}")

        stmt = select(Site).where(Site.owner_id == owner_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, site: Site) -> Site:
        """Persist a new Site and return the refreshed instance."""
        logger.info("Creating Site.")
        logger.debug(f"slug={site.slug} owner_id={site.owner_id}")

        self.session.add(site)
        await self.session.flush()
        await self.session.refresh(site)
        return site

    async def list(self, query: ListSiteQuery | None = None) -> Sequence[Site]:
        """Return all sites, with optional filters from a ListSiteQuery."""
        logger.info("Listing Sites.")
        logger.debug(f"query={query}")

        stmt = select(Site)
        if query:
            if query.owner_id is not None:
                stmt = stmt.where(Site.owner_id == query.owner_id)
            if query.status is not None:
                stmt = stmt.where(Site.status == query.status)
            if query.visibility is not None:
                stmt = stmt.where(Site.visibility == query.visibility)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete(self, site: Site) -> Site:
        """Delete the given Site and return the deleted instance."""
        logger.info("Deleting Site.")
        logger.debug(f"site_id={site.id}")

        await self.session.delete(site)
        await self.session.flush()
        return site
