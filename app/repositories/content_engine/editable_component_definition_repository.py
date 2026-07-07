from typing import Optional, Sequence

from sqlmodel import select
from app.db.models import EditableComponentDefinition
from app.shared.enums import EditableComponentKind
from sqlalchemy.ext.asyncio import AsyncSession


class EditableComponentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, solution: EditableComponentDefinition
    ) -> EditableComponentDefinition:
        self.session.add(solution)
        await self.session.flush()
        await self.session.refresh(solution)
        return solution

    async def get(self, solution_id: str) -> Optional[EditableComponentDefinition]:
        stmt = select(EditableComponentDefinition).where(
            EditableComponentDefinition.id == solution_id
        )
        result = await self.session.execute(stmt)
        solution = result.scalar_one_or_none()
        return solution

    async def get_by_key(self, key: str) -> Optional[EditableComponentDefinition]:
        stmt = select(EditableComponentDefinition).where(
            EditableComponentDefinition.key == key
        )
        result = await self.session.execute(stmt)
        solution = result.scalar_one_or_none()
        return solution

    async def list(
        self,
        kind: Optional[EditableComponentKind] = None,
    ) -> Sequence[EditableComponentDefinition]:
        stmt = select(EditableComponentDefinition)
        if kind:
            stmt = stmt.where(EditableComponentDefinition.kind == kind)

        result = await self.session.execute(stmt)
        solutions = result.scalars().all()
        return solutions

    async def delete(
        self, solution: EditableComponentDefinition
    ) -> EditableComponentDefinition:
        await self.session.delete(solution)
        await self.session.flush()
        return solution
