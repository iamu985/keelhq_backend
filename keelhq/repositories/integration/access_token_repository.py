"""Access token repository.

Responsibility:
- Provide all database read and write operations for the AccessToken model.
- Remain free of business logic and exception handling.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from keelhq.core.logger import logger
from keelhq.db.models import AccessToken


# TODO: add unit tests for this repository
class AccessTokenRepository:
    """Data access layer for the AccessToken model.

    Responsibility:
    - Execute parameterised SQL queries against the access_tokens table.
    - Return domain model instances or sequences; never raw rows or dicts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, token_id: UUID) -> AccessToken | None:
        """Return the access token with the given primary key, or None if not found."""
        logger.info("Fetching AccessToken by id.")
        logger.debug(f"token_id={token_id}")

        stmt = select(AccessToken).where(AccessToken.id == token_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_token_hash(self, token_hash: str) -> AccessToken | None:
        """Return the access token whose hash matches, or None if not found.

        This is the primary lookup used during request authentication. The raw
        token is hashed by the caller before passing it here.
        """
        logger.info("Fetching AccessToken by token_hash.")

        stmt = select(AccessToken).where(AccessToken.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_site(
        self,
        site_id: UUID,
        is_active: bool | None = None,
    ) -> Sequence[AccessToken]:
        """Return all tokens for a site, with optional is_active filter."""
        logger.info("Listing AccessTokens by site_id.")
        logger.debug(f"site_id={site_id} is_active={is_active}")

        stmt = select(AccessToken).where(AccessToken.site_id == site_id)
        if is_active is not None:
            stmt = stmt.where(AccessToken.is_active == is_active)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, token: AccessToken) -> AccessToken:
        """Persist a new AccessToken and return the refreshed instance."""
        logger.info("Creating AccessToken.")
        logger.debug(f"site_id={token.site_id} name={token.name}")

        self.session.add(token)
        await self.session.flush()
        await self.session.refresh(token)
        return token

    async def delete(self, token: AccessToken) -> AccessToken:
        """Delete the given AccessToken and return the deleted instance."""
        logger.info("Deleting AccessToken.")
        logger.debug(f"token_id={token.id}")

        await self.session.delete(token)
        await self.session.flush()
        return token
