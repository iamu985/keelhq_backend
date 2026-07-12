"""Editable component definition repository.

Responsibility:
- Provide all database read and write operations for the EditableComponentDefinition model.
- Remain free of business logic and exception handling.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.logger import logger
from app.db.models import EditableComponentDefinition
from app.shared.enums import EditableComponentKind


# TODO: add unit tests for this repository
class EditableComponentDefinitionRepository:
    """Data access layer for the EditableComponentDefinition model.

    Responsibility:
    - Execute parameterised SQL queries against the editable_component_definitions table.
    - Return domain model instances or sequences; never raw rows or dicts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, definition_id: UUID) -> EditableComponentDefinition | None:
        """Return the definition with the given primary key, or None if not found."""
        logger.info("Fetching EditableComponentDefinition by id.")
        logger.debug(f"definition_id={definition_id}")

        stmt = select(EditableComponentDefinition).where(
            EditableComponentDefinition.id == definition_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_site_and_key(
        self, site_id: UUID, key: str
    ) -> EditableComponentDefinition | None:
        """Return the definition within a site that matches the given key, or None.

        Key uniqueness is scoped per site, so both site_id and key are required.
        """
        logger.info("Fetching EditableComponentDefinition by site_id and key.")
        logger.debug(f"site_id={site_id} key={key}")

        stmt = select(EditableComponentDefinition).where(
            EditableComponentDefinition.site_id == site_id,
            EditableComponentDefinition.key == key,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_site(
        self,
        site_id: UUID,
        kind: EditableComponentKind | None = None,
    ) -> Sequence[EditableComponentDefinition]:
        """Return all definitions for a site, with optional kind filter."""
        logger.info("Listing EditableComponentDefinitions by site_id.")
        logger.debug(f"site_id={site_id} kind={kind}")

        stmt = select(EditableComponentDefinition).where(
            EditableComponentDefinition.site_id == site_id
        )
        if kind is not None:
            stmt = stmt.where(EditableComponentDefinition.kind == kind)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, definition: EditableComponentDefinition) -> EditableComponentDefinition:
        """Persist a new EditableComponentDefinition and return the refreshed instance."""
        logger.info("Creating EditableComponentDefinition.")
        logger.debug(f"site_id={definition.site_id} key={definition.key}")

        self.session.add(definition)
        await self.session.flush()
        await self.session.refresh(definition)
        return definition

    async def delete(self, definition: EditableComponentDefinition) -> EditableComponentDefinition:
        """Delete the given EditableComponentDefinition and return the deleted instance."""
        logger.info("Deleting EditableComponentDefinition.")
        logger.debug(f"definition_id={definition.id}")

        await self.session.delete(definition)
        await self.session.flush()
        return definition
