"""Content Engine — ContentEntry Pydantic schemas.

Responsibility:
- Define API contracts for creating and querying ContentEntry resources.
- Keep schemas decoupled from ORM models.
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.shared.enums import ContentStatus


class CreateContentEntry(BaseModel):
    """Input contract for creating a new content entry.

    Responsibility:
    - Validate all required fields before the repository persists the record.
    """

    site_id: UUID
    definition_id: UUID
    title: str | None = None
    slug: str | None = None
    status: ContentStatus = ContentStatus.DRAFT
    sort_order: int = 0
    content: dict[str, Any] = {}


class ListContentEntryQuery(BaseModel):
    """Query filter contract for listing content entries.

    Responsibility:
    - Carry optional filter parameters from the service layer to the repository.
    """

    site_id: UUID | None = None
    definition_id: UUID | None = None
    status: ContentStatus | None = None
