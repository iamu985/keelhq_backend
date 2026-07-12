"""Form repository.

Responsibility:
- Provide all database read and write operations for the Form model.
- Remain free of business logic and exception handling.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from keelhq.core.logger import logger
from keelhq.db.models import Form


# TODO: add unit tests for this repository
class FormRepository:
    """Data access layer for the Form model.

    Responsibility:
    - Execute parameterised SQL queries against the forms table.
    - Return domain model instances or sequences; never raw rows or dicts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, form_id: UUID) -> Form | None:
        """Return the form with the given primary key, or None if not found."""
        logger.info("Fetching Form by id.")
        logger.debug(f"form_id={form_id}")

        stmt = select(Form).where(Form.id == form_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_site_and_slug(self, site_id: UUID, slug: str) -> Form | None:
        """Return the form within a site that matches the given slug, or None.

        Slug uniqueness is scoped per site, so both site_id and slug are required.
        """
        logger.info("Fetching Form by site_id and slug.")
        logger.debug(f"site_id={site_id} slug={slug}")

        stmt = select(Form).where(
            Form.site_id == site_id,
            Form.slug == slug,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_site(
        self,
        site_id: UUID,
        is_active: bool | None = None,
    ) -> Sequence[Form]:
        """Return all forms for a site, with optional is_active filter."""
        logger.info("Listing Forms by site_id.")
        logger.debug(f"site_id={site_id} is_active={is_active}")

        stmt = select(Form).where(Form.site_id == site_id)
        if is_active is not None:
            stmt = stmt.where(Form.is_active == is_active)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, form: Form) -> Form:
        """Persist a new Form and return the refreshed instance."""
        logger.info("Creating Form.")
        logger.debug(f"site_id={form.site_id} slug={form.slug}")

        self.session.add(form)
        await self.session.flush()
        await self.session.refresh(form)
        return form

    async def delete(self, form: Form) -> Form:
        """Delete the given Form and return the deleted instance."""
        logger.info("Deleting Form.")
        logger.debug(f"form_id={form.id}")

        await self.session.delete(form)
        await self.session.flush()
        return form
