from typing import Optional, Sequence

from sqlmodel import select
from app.db.models import Solution
from sqlalchemy.ext.asyncio import AsyncSession


class SolutionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, solution: Solution) -> Solution:
        self.session.add(solution)
        await self.session.flush()
        await self.session.refresh(solution)
        return solution

    async def get(self, solution_id: str) -> Optional[Solution]:
        stmt = select(Solution).where(Solution.id == solution_id)
        result = await self.session.execute(stmt)
        solution = result.scalar_one_or_none()
        return solution

    async def get_by_name(self, solution_name: str) -> Optional[Solution]:
        stmt = select(Solution).where(Solution.name == solution_name)
        result = await self.session.execute(stmt)
        solution = result.scalar_one_or_none()
        return solution

    async def get_by_slug(self, solution_slug: str) -> Optional[Solution]:
        stmt = select(Solution).where(Solution.slug == solution_slug)
        result = await self.session.execute(stmt)
        solution = result.scalar_one_or_none()
        return solution

    async def list(self) -> Sequence[Solution]:
        stmt = select(Solution)
        result = await self.session.execute(stmt)
        solutions = result.scalars().all()
        return solutions

    async def delete(self, solution: Solution) -> Solution:
        await self.session.delete(solution)
        await self.session.flush()
        return solution
