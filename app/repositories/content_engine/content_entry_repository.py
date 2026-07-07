from typing import Optional, Sequence

from sqlmodel import select
from app.db.models import ContentEntry
from sqlalchemy.ext.asyncio import AsyncSession


class ContentEntryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, solution: ContentEntry) -> ContentEntry:
        self.session.add(solution)
        await self.session.flush()
        await self.session.refresh(solution)
        return solution

    async def get(self, solution_id: str) -> Optional[ContentEntry]:
        stmt = select(ContentEntry).where(ContentEntry.id == solution_id)
        result = await self.session.execute(stmt)
        solution = result.scalar_one_or_none()
        return solution

    async def get_by_definition(self, definition_id: str) -> Optional[ContentEntry]:
        stmt = select(ContentEntry).where(ContentEntry.definition_id == definition_id)
        result = await self.session.execute(stmt)
        solution = result.scalar_one_or_none()
        return solution

    async def get_by_slug(self, solution_slug: str) -> Optional[ContentEntry]:
        stmt = select(ContentEntry).where(ContentEntry.slug == solution_slug)
        result = await self.session.execute(stmt)
        solution = result.scalar_one_or_none()
        return solution

    async def list(self) -> Sequence[ContentEntry]:
        stmt = select(ContentEntry)
        result = await self.session.execute(stmt)
        solutions = result.scalars().all()
        return solutions

    async def delete(self, solution: ContentEntry) -> ContentEntry:
        await self.session.delete(solution)
        await self.session.flush()
        return solution
