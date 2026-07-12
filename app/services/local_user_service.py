"""Local user use-case service.

Responsibility:
- Orchestrate create, list, and detail operations for local users.
"""

from uuid import UUID

from app.core.unit_of_work import AbstractUnitOfWork
from app.schemas.identity import CreateLocalUser, LocalUserDetail
from app.utils.mappers import LocalUserMapper


class LocalUserService:
    """Application service for local user CRUD/listing."""

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def create(self, payload: CreateLocalUser) -> LocalUserDetail | None:
        """Create a new local user and commit the transaction."""
        user = LocalUserMapper.from_create(payload)
        await self.uow.users.create(user)
        await self.uow.commit()
        return LocalUserMapper.to_detail(user)

    async def list(self) -> list[LocalUserDetail]:
        """Return a list of all local users."""
        users = await self.uow.users.list()
        return LocalUserMapper.to_list(users)

    async def get_by_id(self, user_id: UUID) -> LocalUserDetail | None:
        """Return the detail for a single local user, or None if not found."""
        user = await self.uow.users.get(user_id=user_id)
        if user is None:
            return None
        return LocalUserMapper.to_detail(user)
