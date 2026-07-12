"""Verification Code repository

Responsiblity:
- Provide all database read, write and update operations for VerificationCode model.
- It is free of business logic and exception handling.
"""

from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.core.logger import logger
from app.db.models import VerificationCode


class VerificationCodeRepository:
    """Data access layer for VerificationCodeRepository model.

    Responsiblity:
    - Execute parameterised SQL queries against the verification code table.
    - Return domain model instances or sequences; never raw rows or dicts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id_: UUID) -> Optional[VerificationCode]:
        logger.info("Fetching VerificationCode by ID.")
        logger.debug(f"id_: {id_}")
        stmt = select(VerificationCode).where(VerificationCode.id == id_)
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

        self.session.add(VerificationCode)
        await self.session.flush()
        await self.session.refresh(verification_code)
        return verification_code

    async def delete(self, verification_code: VerificationCode) -> VerificationCode:
        logger.info("Deleting VerificationCode.")
        logger.debug(f"id={verification_code.id}")

        await self.session.delete(verification_code)
        await self.session.flush()
        return verification_code
