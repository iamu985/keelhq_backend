"""Editable component definition model.

Responsibility:
- Define the database schema for editable component templates that belong to a site.

This model answers the question: "What parts of this website can be edited?" It
never stores user content. Instead, it describes the structure that the dashboard
uses to generate an editing interface. The actual values edited by users live in
`ContentEntry` and are validated against this definition at the application layer.
"""

from typing import TYPE_CHECKING, Any

from sqlalchemy import Column, Enum, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from keelhq.db.models.mixins import BaseModel, IsPartOfSite, IsPartOfSolution
from keelhq.shared.enums import EditableComponentKind

if TYPE_CHECKING:
    from keelhq.db.models.content_engine.content_entry import ContentEntry
    from keelhq.db.models.site_management.site import Site
    from keelhq.db.models.site_management.solution import Solution


# TODO: add unit tests for this model
class EditableComponentDefinition(BaseModel, IsPartOfSite, IsPartOfSolution, table=True):
    """A template describing one editable section of a site.

    Responsibility:
    - Tell the dashboard how to generate an editor for a specific website section.
    - Link the section to the site it belongs to and the solution that provided it.

    Users never edit `editor_schema` manually. The schema is populated when a site
    installs a Solution, and may be extended by AI agents in the future. Keeping
    the structure separate from the values makes it possible to change a form
    definition without touching existing content, and to render different
    dashboards for the same underlying data.
    """

    __tablename__ = "editable_component_definitions"  # pyright: ignore

    key: str = Field(
        nullable=False,
        index=True,
        description="Internal identifier for this component within a site (e.g., 'hero').",
    )
    display_name: str = Field(
        nullable=False,
        description="Human-readable label shown in the dashboard sidebar (e.g., 'Hero').",
    )
    description: str | None = Field(
        default=None,
        description="Optional explanation of what this component represents.",
    )
    kind: EditableComponentKind = Field(
        sa_column=Column(
            Enum(EditableComponentKind),
            nullable=False,
            index=True,
        ),
        description="Cardinality of this component: singleton or collection.",
    )
    display_order: int = Field(
        default=0,
        nullable=False,
        index=True,
        description="Position in the dashboard sidebar; lower values appear first.",
    )
    icon: str | None = Field(
        default=None,
        description="Optional icon identifier used by the dashboard.",
    )

    # `editor_schema` is NOT JSON Schema. It is an internal dashboard description
    # that tells the dashboard how to build the editing form for this component.
    # Each item is a field definition (key, label, type, required, etc.). The
    # dashboard consumes these items to render inputs, while `ContentEntry.content`
    # stores the actual values produced by those inputs. This separation is the core
    # of the Content Engine: structure lives here, values live in ContentEntry.
    editor_schema: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False),
        description="Internal dashboard field definitions for generating the editor UI.",
    )

    # Relationships.
    # A definition belongs to exactly one site and one solution template, and may
    # have many content entries depending on its kind (singletons usually have one,
    # collections may have many).
    site: "Site" = Relationship(back_populates="definitions")
    solution: "Solution" = Relationship(back_populates="definitions")
    entries: list["ContentEntry"] = Relationship(back_populates="definition")

    __table_args__ = (  # pyright: ignore
        UniqueConstraint("site_id", "key", name="uq_editable_component_definitions_site_id_key"),
        Index("ix_editable_component_definitions_site_id_kind", "site_id", "kind"),
        Index(
            "ix_editable_component_definitions_site_id_display_order",
            "site_id",
            "display_order",
        ),
    )
