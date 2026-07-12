"""Verification Code repository

Responsiblity:
- Provide all database read, write and update operations for VerificationCode model.
- It is free of business logic and exception handling.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from keelhq.core.logger import logger
from keelhq.db.models import VerificationCode


class VerificationCodeRepository:
    """Data access layer for VerificationCodeRepository model.

    Responsiblity:
    - Execute parameterised SQL queries against the verification code table.
    - Return domain model instances or sequences; never raw rows or dicts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id_: UUID) -> VerificationCode | None:
        logger.info("Fetching VerificationCode by ID.")
        logger.debug(f"id_: {id_}")
        stmt = select(VerificationCode).where(VerificationCode.id == id_)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: int) -> VerificationCode | None:
        """Fetch verification code by its numeric value."""
        logger.info("Fetching VerificationCode by code.")
        logger.debug(f"code: {code}")
        stmt = select(VerificationCode).where(VerificationCode.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_unused_code_for_user(
        self, local_user_id: UUID, code: int
    ) -> VerificationCode | None:
        """Fetch unused verification code for a specific user."""
        logger.info("Fetching unused VerificationCode for user.")
        logger.debug(f"local_user_id: {local_user_id}, code: {code}")
        stmt = select(VerificationCode).where(
            VerificationCode.local_user_id == local_user_id,
            VerificationCode.code == code,
            not VerificationCode.is_used,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self) -> Sequence[VerificationCode]:
        """Return all verification codes. Never to be used or exposed publicly."""
        logger.info("Listing all VerificationCodes")
        stmt = select(VerificationCode)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, verification_code: VerificationCode) -> VerificationCode:
        logger.info("Creating VerificationCode.")

        self.session.add(verification_code)
        await self.session.flush()
        await self.session.refresh(verification_code)
        return verification_code

    async def mark_as_used(self, verification_code: VerificationCode) -> VerificationCode:
        """Mark a verification code as used."""
        logger.info("Marking VerificationCode as used.")
        logger.debug(f"id={verification_code.id}")

        verification_code.is_used = True
        await self.session.flush()
        await self.session.refresh(verification_code)
        return verification_code

    async def delete(self, verification_code: VerificationCode) -> VerificationCode:
        logger.info("Deleting VerificationCode.")
        logger.debug(f"id={verification_code.id}")

        await self.session.delete(verification_code)
        await self.session.flush()
        return verification_code
