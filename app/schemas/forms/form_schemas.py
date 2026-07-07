"""Forms — Form Pydantic schemas.

Responsibility:
- Define API contracts for creating and querying Form resources.
- Keep schemas decoupled from ORM models.
"""

from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class CreateForm(BaseModel):
    """Input contract for creating a new form.

    Responsibility:
    - Validate all required fields before the repository persists the record.
    """

    site_id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    field_schema: list[dict[str, Any]] = []
    settings: dict[str, Any] = {}
    is_active: bool = True


class ListFormQuery(BaseModel):
    """Query filter contract for listing forms.

    Responsibility:
    - Carry optional filter parameters from the service layer to the repository.
    """

    site_id: Optional[UUID] = None
    is_active: Optional[bool] = None
