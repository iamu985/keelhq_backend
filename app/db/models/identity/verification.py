"""
Verification model for development-only authentication

Responsiblity:
- Define the database schema for verification of the local user for development user accounts.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import Column, DateTime
from sqlmodel import Field

from app.db.models.mixins import BaseModel


def expires_in_15_minutes() -> datetime:
    return datetime.now(UTC) + timedelta(minutes=15)


class VerificationCode(BaseModel, table=True):
    """Development-only verification code."""

    __tablename__ = "verification_codes"  # pyright: ignore

    code: int = Field(max_digits=6, unique=True, index=True, nullable=False)
    expires_at: datetime = Field(
        default_factory=expires_in_15_minutes,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    is_used: bool = Field(default=False, nullable=False)

    #  Relationship with local_user
    local_user_id: UUID = Field(foreign_key="local_users.id", nullable=False, index=True)
