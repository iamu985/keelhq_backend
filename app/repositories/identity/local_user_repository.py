from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.logger import logger
from app.db.models import LocalUser


class LocalUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: UUID) -> Optional[LocalUser]:
        logger.info("Getting user via user_id.")
        logger.debug(f"Received USER_ID: {user_id}")

        stmt = select(LocalUser).where(LocalUser.id == user_id)
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[LocalUser]:
        stmt = select(LocalUser).where(LocalUser.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[LocalUser]:
        stmt = select(LocalUser).where(LocalUser.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: LocalUser) -> Optional[LocalUser]:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def list(self) -> Sequence[LocalUser]:
        stmt = select(LocalUser)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return users

    async def delete(self, user: LocalUser) -> LocalUser:
        await self.session.delete(user)
        await self.session.flush()
        return user
