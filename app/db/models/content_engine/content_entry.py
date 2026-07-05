"""Content entry model.

Responsibility:
- Define the database schema for storing actual user-generated content values.

A ContentEntry holds the values that the frontend consumes. The editable structure
for those values comes from `EditableComponentDefinition.editor_schema`. This split
keeps the domain models technology-agnostic: no framework-specific rendering,
CMS schema design, or AI logic lives in this model.
"""

from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import Column, Enum, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.shared.enums import ContentStatus

from app.db.models.mixins import BaseModel, IsPartOfSite

if TYPE_CHECKING:
    from app.db.models.content_engine.editable_component_definition import EditableComponentDefinition
    from app.db.models.site_management.site import Site


# TODO: add unit tests for this model
class ContentEntry(BaseModel, IsPartOfSite, table=True):
    """A single piece of user-generated content for a site.

    Responsibility:
    - Store the actual values that make up an editable website section.
    - Track publish state, ordering, and optional routing metadata.

    This model stores ONLY values. The shape of those values is dictated by the
    linked `EditableComponentDefinition`. For example, a Hero definition might
    expect `headline`, `subtitle`, and `button`, while a Product definition might
    expect `name`, `price`, and `image`. The dashboard uses the definition to
    generate the form and this model to persist the result.
    """

    __tablename__ = "content_entries"  # pyright: ignore

    definition_id: UUID = Field(
        foreign_key="editable_component_definitions.id",
        index=True,
        nullable=False,
        description="The editable component definition that describes the structure of this entry.",
    )
    title: Optional[str] = Field(
        default=None,
        index=True,
        description="Human-readable title shown in the dashboard list (e.g., 'SEO Optimization').",
    )
    slug: Optional[str] = Field(
        default=None,
        description="Optional URL-safe identifier for future routing (e.g., 'seo-optimization').",
    )
    status: ContentStatus = Field(
        default=ContentStatus.DRAFT,
        sa_column=Column(
            Enum(ContentStatus),
            nullable=False,
            index=True,
        ),
        description="Publication state of this entry.",
    )
    sort_order: int = Field(
        default=0,
        nullable=False,
        index=True,
        description="Ordering within a collection; singletons use 0.",
    )

    # `content` stores the actual values produced by the dashboard editor. It is a
    # free-form JSONB object whose keys match the `key` values declared in the
    # parent `EditableComponentDefinition.editor_schema`. Because the structure is
    # defined separately, the same content model can represent a Hero, a Service, a
    # Product, or any other component without schema changes.
    content: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
        description="User-generated values for this content entry.",
    )

    # Relationships.
    # Every entry belongs to a site and to the definition that describes its shape.
    site: "Site" = Relationship(back_populates="content_entries")
    definition: "EditableComponentDefinition" = Relationship(back_populates="entries")

    __table_args__ = (  # pyright: ignore
        # Slug uniqueness is scoped to the site so that future routing can rely on
        # a single site-level namespace. PostgreSQL allows multiple NULLs in a unique
        # constraint, so optional slugs do not conflict.
        UniqueConstraint("site_id", "slug", name="uq_content_entries_site_id_slug"),
        Index("ix_content_entries_site_id_status", "site_id", "status"),
        Index("ix_content_entries_definition_id_status", "definition_id", "status"),
        Index("ix_content_entries_definition_id_sort_order", "definition_id", "sort_order"),
        Index("ix_content_entries_title", "title"),
    )
