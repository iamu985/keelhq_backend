"""Local user repository.

Responsibility:
- Provide all database read and write operations for the LocalUser model.
- Remain free of business logic and exception handling; those belong to the service layer.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from keelhq.core.logger import logger
from keelhq.db.models import LocalUser


# TODO: add unit tests for this repository
class LocalUserRepository:
    """Data access layer for the LocalUser model.

    Responsibility:
    - Execute parameterised SQL queries against the local_users table.
    - Return domain model instances or sequences; never raw rows or dicts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: UUID) -> LocalUser | None:
        """Return the user with the given primary key, or None if not found."""
        logger.info("Fetching LocalUser by id.")
        logger.debug(f"user_id={user_id}")

        stmt = select(LocalUser).where(LocalUser.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> LocalUser | None:
        """Return the user with the given email address, or None if not found."""
        logger.info("Fetching LocalUser by email.")
        logger.debug(f"email={email}")

        stmt = select(LocalUser).where(LocalUser.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> LocalUser | None:
        """Return the user with the given username, or None if not found."""
        logger.info("Fetching LocalUser by username.")
        logger.debug(f"username={username}")

        stmt = select(LocalUser).where(LocalUser.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: LocalUser) -> LocalUser:
        """Persist a new LocalUser and return the refreshed instance."""
        logger.info("Creating LocalUser.")
        logger.debug(f"email={user.email} username={user.username}")

        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def list(self) -> Sequence[LocalUser]:
        """Return all local users."""
        logger.info("Listing all LocalUsers.")

        stmt = select(LocalUser)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete(self, user: LocalUser) -> LocalUser:
        """Delete the given LocalUser and return the deleted instance."""
        logger.info("Deleting LocalUser.")
        logger.debug(f"user_id={user.id}")

        await self.session.delete(user)
        await self.session.flush()
        return user
