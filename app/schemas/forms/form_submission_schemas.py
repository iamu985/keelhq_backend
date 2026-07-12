"""Forms — FormSubmission Pydantic schemas.

Responsibility:
- Define API contracts for creating and querying FormSubmission resources.
- Keep schemas decoupled from ORM models.
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.shared.enums import FormSubmissionStatus


class CreateFormSubmission(BaseModel):
    """Input contract for creating a new form submission.

    Responsibility:
    - Validate all required fields before the repository persists the record.
    """

    form_id: UUID
    payload: dict[str, Any] = {}
    ip_address: str | None = None
    user_agent: str | None = None


class ListFormSubmissionQuery(BaseModel):
    """Query filter contract for listing form submissions.

    Responsibility:
    - Carry optional filter parameters from the service layer to the repository.
    """

    form_id: UUID | None = None
    status: FormSubmissionStatus | None = None
