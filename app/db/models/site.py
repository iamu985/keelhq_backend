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
from .base import BaseModel


# TODO: add unit tests for this model
class Site(BaseModel, table=True):
    __tablename__ = "sites"  # pyright: ignore

    owner_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True), ForeignKey("local_users.id"), nullable=False
        ),
    )
    name: str = Field(nullable=False)
    slug: str = Field(unique=True, nullable=False)
    description: Optional[str] = Field(default=None, max_length=250)
    logo_url: Optional[str] = Field(default=None)
    status: str = Field(nullable=False)
    visibility: str = Field(nullable=False)
    extension_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PGUUID(as_uuid=True), nullable=True),
    )
