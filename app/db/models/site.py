"""Site model.

Responsibility:
- Define the database schema for the sites table.
"""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, Relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .content_entry import ContentEntry
    from .editable_component_definition import EditableComponentDefinition


# TODO: add unit tests for this model
class Site(BaseModel, table=True):
    __tablename__ = "sites"  # pyright: ignore

    owner_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True), ForeignKey("local_users.id"), nullable=False, index=True
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

    # Content Engine relationships.
    # A site owns the component definitions that describe its editable sections,
    # and the content entries that store the actual values for those sections.
    definitions: list["EditableComponentDefinition"] = Relationship(
        back_populates="site",
    )
    content_entries: list["ContentEntry"] = Relationship(
        back_populates="site",
    )
