"""Form model.

Responsibility:
- Define the database schema for editable forms on a website.

A Form describes a set of fields that visitors can fill out (e.g., Contact, Appointment,
Waitlist). The actual field definitions live in `schema` and the submitted values live in
`FormSubmission.payload`. This separation lets the dashboard generate an editor for the
form structure without touching the data collected by visitors.
"""

from typing import TYPE_CHECKING, Any

from sqlalchemy import Column, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.db.models.mixins import BaseModel, IsPartOfSite

if TYPE_CHECKING:
    from app.db.models.forms.form_submission import FormSubmission
    from app.db.models.site_management.site import Site


# TODO: add unit tests for this model
class Form(BaseModel, IsPartOfSite, table=True):
    """An editable form that belongs to a site.

    Responsibility:
    - Describe the fields and behavior of a website form.
    - Collect submissions without storing the submitted data itself.
    """

    __tablename__ = "forms"  # pyright: ignore

    name: str = Field(
        nullable=False,
        description="Human-readable name shown in the dashboard (e.g., 'Contact Form').",
    )
    slug: str = Field(
        nullable=False,
        index=True,
        description="URL-safe identifier for the form within a site.",
    )
    description: str | None = Field(
        default=None,
        description="Optional explanation of the form's purpose.",
    )
    # NOTE: The Python attribute is named `field_schema` because `schema` shadows a
    # SQLModel/SQLAlchemy attribute on the base class. The underlying database
    # column keeps the requested name `schema` for consistency with the domain.
    field_schema: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column("schema", JSONB, nullable=False),
        description="Field definitions that the dashboard uses to render the form editor.",
    )
    settings: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
        description="Behavioral configuration (e.g., notifications, redirect URL, CAPTCHA).",
    )
    is_active: bool = Field(
        default=True,
        nullable=False,
        description="Whether the form is currently accepting submissions.",
    )

    # Relationships.
    # A form belongs to one site and may collect many submissions.
    site: "Site" = Relationship(back_populates="forms")
    submissions: list["FormSubmission"] = Relationship(back_populates="form")

    __table_args__ = (  # pyright: ignore
        UniqueConstraint("site_id", "slug", name="uq_forms_site_id_slug"),
        Index("ix_forms_site_id", "site_id"),
        Index("ix_forms_slug", "slug"),
    )
