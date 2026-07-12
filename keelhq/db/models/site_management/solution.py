"""Solution model.

Responsibility:
- Define the database schema for installable website solution templates.

A Solution is a template that describes which editable components should exist for
a particular website domain (e.g., Business, Portfolio, Commerce). It does NOT
store any user-generated content. The actual content lives in `ContentEntry` and is
linked to the `EditableComponentDefinition` rows that a Solution provides.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship

from keelhq.db.models.mixins import BaseModel

if TYPE_CHECKING:
    from keelhq.db.models.content_engine.editable_component_definition import (
        EditableComponentDefinition,
    )


# TODO: add unit tests for this model
class Solution(BaseModel, table=True):
    """An installable website solution template.

    Responsibility:
    - Describe a set of editable component definitions that a site may use.
    - Stay decoupled from any user content or site-specific data.

    Think of a Solution as a domain blueprint: it tells Keel which sections of a
    website (Hero, About, Services, Products, etc.) should be editable and how the
    dashboard should generate editors for those sections. The dashboard and AI
    agents consume Solution definitions, while the frontend consumes the content
    values stored separately in `ContentEntry`.
    """

    __tablename__ = "solutions"  # pyright: ignore

    name: str = Field(
        nullable=False,
        index=True,
        description="Internal name of the solution (e.g., 'business').",
    )
    slug: str = Field(
        nullable=False,
        description="URL-safe identifier used to select a solution (e.g., 'business').",
    )
    display_name: str = Field(
        nullable=False,
        description="Human-readable name shown in the dashboard (e.g., 'Business').",
    )
    description: str | None = Field(
        default=None,
        description="Short explanation of the solution's purpose and target audience.",
    )
    icon: str | None = Field(
        default=None,
        description="Optional icon identifier used by the dashboard.",
    )
    version: str = Field(
        default="0.1.0",
        nullable=False,
        description="Version of the solution template (e.g., '1.0.0').",
    )
    is_builtin: bool = Field(
        default=True,
        description="Whether this solution is shipped by Keel or created by a user/AI agent.",
    )

    # A Solution is a template, so it may define many editable component templates.
    definitions: list["EditableComponentDefinition"] = Relationship(
        back_populates="solution",
    )

    __table_args__ = (  # pyright: ignore
        UniqueConstraint("slug", name="uq_solutions_slug"),
        Index("ix_solutions_name", "name"),
        Index("ix_solutions_is_builtin", "is_builtin"),
    )
