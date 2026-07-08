"""Solution repository.

Responsibility:
- Provide all database read and write operations for the Solution model.
- Remain free of business logic and exception handling.
"""

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.logger import logger
from app.db.models import Solution
from app.schemas.site_management.solution_schemas import ListSolutionQuery


# TODO: add unit tests for this repository
class SolutionRepository:
    """Data access layer for the Solution model.

    Responsibility:
    - Execute parameterised SQL queries against the solutions table.
    - Return domain model instances or sequences; never raw rows or dicts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, solution_id: UUID) -> Optional[Solution]:
        """Return the solution with the given primary key, or None if not found."""
        logger.info("Fetching Solution by id.")
        logger.debug(f"solution_id={solution_id}")

        stmt = select(Solution).where(Solution.id == solution_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Solution]:
        """Return the solution with the given unique slug, or None if not found."""
        logger.info("Fetching Solution by slug.")
        logger.debug(f"slug={slug}")

        stmt = select(Solution).where(Solution.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Solution]:
        """Return the solution with the given name, or None if not found."""
        logger.info("Fetching Solution by name.")
        logger.debug(f"name={name}")

        stmt = select(Solution).where(Solution.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, solution: Solution) -> Solution:
        """Persist a new Solution and return the refreshed instance."""
        logger.info("Creating Solution.")
        logger.debug(f"slug={solution.slug}")

        self.session.add(solution)
        await self.session.flush()
        await self.session.refresh(solution)
        return solution

    async def list(
        self, query: Optional[ListSolutionQuery] = None
    ) -> Sequence[Solution]:
        """Return all solutions, with optional filters from a ListSolutionQuery."""
        logger.info("Listing Solutions.")
        logger.debug(f"query={query}")

        stmt = select(Solution)
        if query and query.is_builtin is not None:
            stmt = stmt.where(Solution.is_builtin == query.is_builtin)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete(self, solution: Solution) -> Solution:
        """Delete the given Solution and return the deleted instance."""
        logger.info("Deleting Solution.")
        logger.debug(f"solution_id={solution.id}")

        await self.session.delete(solution)
        await self.session.flush()
        return solution
