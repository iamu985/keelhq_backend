"""Base SQLModel abstractions.

Responsibility:
- Provide reusable mixins and a base model for all database tables.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel


# TODO: add unit tests for this model
class UUIDMixin(SQLModel, table=False):
    """Mixin that adds a UUID primary key.

    Responsibility:
    - Provide a reusable, PostgreSQL-compatible UUID primary key field.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)


class IsPartOfSolution(SQLModel, table=False):
    """
    Mixin that adds a FOREIGN KEY relation to solutions.

    Responsibility:
    - Provide a reusable, PostgreSQL-compatible fk relation.
    """

    solution_id: UUID = Field(foreign_key="solutions.id")


class IsPartOfSite(SQLModel, table=False):
    site_id: UUID = Field(foreign_key="sites.id")


# TODO: add unit tests for this model
class TimestampMixin(SQLModel, table=False):
    """Mixin that adds created/updated timestamp fields.

    Responsibility:
    - Provide consistent audit timestamp fields for database tables.
    """

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
    )


# TODO: add unit tests for this model
class BaseModel(UUIDMixin, TimestampMixin, SQLModel, table=False):
    """Base model combining UUID and timestamp mixins.

    Responsibility:
    - Serve as the common base for all table models in the application.
    """
