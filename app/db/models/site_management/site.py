"""Site model.

Responsibility:
- Define the database schema for the sites table.
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, Relationship

from app.db.models.mixins import BaseModel

if TYPE_CHECKING:
    from app.db.models.content_engine.content_entry import ContentEntry
    from app.db.models.content_engine.editable_component_definition import (
        EditableComponentDefinition,
    )
    from app.db.models.forms.form import Form
    from app.db.models.integration.access_token import AccessToken
    from app.db.models.media.media_asset import MediaAsset


# TODO: add unit tests for this model
class Site(BaseModel, table=True):
    __tablename__ = "sites"  # pyright: ignore

    owner_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("local_users.id"),
            nullable=False,
            index=True,
        ),
    )
    name: str = Field(nullable=False)
    slug: str = Field(unique=True, nullable=False)
    description: str | None = Field(default=None, max_length=250)
    logo_url: str | None = Field(default=None)
    status: str = Field(nullable=False)
    visibility: str = Field(nullable=False)
    extension_id: UUID | None = Field(
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

    # Media relationship.
    # A site may own many uploaded assets.
    media_assets: list["MediaAsset"] = Relationship(
        back_populates="site",
    )

    # Forms relationship.
    # A site may contain many editable forms, each with its own submissions.
    forms: list["Form"] = Relationship(
        back_populates="site",
    )

    # Integration relationship.
    # A site may have multiple access tokens for external tools and AI agents.
    access_tokens: list["AccessToken"] = Relationship(
        back_populates="site",
    )
