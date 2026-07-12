"""Form submission model.

Responsibility:
- Define the database schema for data submitted through a website form.

A FormSubmission stores the visitor-provided payload for a specific form. The shape
of the payload is dictated by the parent `Form.field_schema`. Keeping the schema and
data separate lets the dashboard evolve forms without migrating historical submissions.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Column, Enum, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from keelhq.db.models.mixins import BaseModel
from keelhq.shared.enums import FormSubmissionStatus

if TYPE_CHECKING:
    from keelhq.db.models.forms.form import Form


# TODO: add unit tests for this model
class FormSubmission(BaseModel, table=True):
    """A single visitor submission for a form.

    Responsibility:
    - Persist the raw payload submitted by a visitor.
    - Track review state and submission context (IP, user agent).
    """

    __tablename__ = "form_submissions"  # pyright: ignore

    form_id: UUID = Field(
        foreign_key="forms.id",
        index=True,
        nullable=False,
        description="The form that received this submission.",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
        description="Values submitted by the visitor, keyed by form field identifiers.",
    )
    status: FormSubmissionStatus = Field(
        default=FormSubmissionStatus.PENDING,
        sa_column=Column(
            Enum(FormSubmissionStatus),
            nullable=False,
            index=True,
        ),
        description="Review state of the submission.",
    )
    submitted_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        description="Moment the visitor submitted the form.",
    )
    ip_address: str | None = Field(
        default=None,
        description="Optional IP address of the submitting visitor.",
    )
    user_agent: str | None = Field(
        default=None,
        description="Optional user agent string of the submitting visitor.",
    )

    # Relationship.
    # Every submission belongs to exactly one form.
    form: "Form" = Relationship(back_populates="submissions")

    __table_args__ = (  # pyright: ignore
        Index("ix_form_submissions_form_id", "form_id"),
        Index("ix_form_submissions_status", "status"),
        Index("ix_form_submissions_submitted_at", "submitted_at"),
    )
