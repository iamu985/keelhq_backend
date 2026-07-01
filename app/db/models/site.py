"""Site model.

Responsibility:
- Define the database schema for the sites table.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel


# TODO: add unit tests for this model
class Site(SQLModel, table=True):
    __tablename__ = "sites"  # pyright: ignore

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PGUUID(as_uuid=True), primary_key=True),
    )
    owner_id: UUID = Field(
        sa_column=Column(PGUUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False),
    )
    name: str = Field(nullable=False)
    slug: str = Field(unique=True, nullable=False)
    description: Optional[str] = Field(default=None, max_length=250)
    logo_url: Optional[str] = Field(default=None)
    status: str = Field(nullable=False)
    visibility: str = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    extension_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PGUUID(as_uuid=True), nullable=True),
    )
