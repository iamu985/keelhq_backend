"""Media asset model.

Responsibility:
- Define the database schema for uploaded media assets.

A MediaAsset is storage-provider agnostic: it stores the metadata needed to locate
and render an uploaded file while the actual bytes live in an external storage
service. This keeps the core domain decoupled from S3, R2, or any other provider.
"""

from typing import TYPE_CHECKING, Any

from sqlalchemy import Column, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.db.models.mixins import BaseModel, IsPartOfSite

if TYPE_CHECKING:
    from app.db.models.site_management.site import Site


# TODO: add unit tests for this model
class MediaAsset(BaseModel, IsPartOfSite, table=True):
    """A single uploaded file belonging to a site.

    Responsibility:
    - Store metadata that describes an uploaded asset (image, video, document, etc.).
    - Remain agnostic to the underlying storage provider.
    """

    __tablename__ = "media_assets"  # pyright: ignore

    filename: str = Field(
        nullable=False,
        description="Original file name shown in the dashboard (e.g., 'hero.jpg').",
    )
    storage_key: str = Field(
        nullable=False,
        unique=True,
        index=True,
        description="Opaque provider-specific key used to retrieve the file bytes.",
    )
    mime_type: str | None = Field(
        default=None,
        description="MIME type of the asset (e.g., 'image/jpeg').",
    )
    extension: str | None = Field(
        default=None,
        description="File extension without the leading dot (e.g., 'jpg').",
    )
    size: int = Field(
        nullable=False,
        description="Size of the file in bytes.",
    )
    width: int | None = Field(
        default=None,
        description="Width in pixels for image/video assets; None for non-visual assets.",
    )
    height: int | None = Field(
        default=None,
        description="Height in pixels for image/video assets; None for non-visual assets.",
    )
    alt_text: str | None = Field(
        default=None,
        description="Accessible description used by frontend renderers.",
    )
    # NOTE: The Python attribute is named `extra_metadata` because `metadata`
    # shadows a SQLAlchemy reserved attribute on the declarative base. The
    # underlying database column keeps the requested name `metadata`.
    extra_metadata: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSONB, nullable=False),
        description="Provider-specific or dashboard metadata (e.g., thumbnails, variants).",
    )

    # Relationship.
    # Every asset belongs to exactly one site.
    site: "Site" = Relationship(back_populates="media_assets")

    __table_args__ = (  # pyright: ignore
        UniqueConstraint("storage_key", name="uq_media_assets_storage_key"),
        Index("ix_media_assets_site_id", "site_id"),
    )
