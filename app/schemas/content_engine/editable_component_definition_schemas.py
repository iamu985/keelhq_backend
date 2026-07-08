"""Content Engine — EditableComponentDefinition Pydantic schemas.

Responsibility:
- Define API contracts for creating and querying EditableComponentDefinition resources.
- Keep schemas decoupled from ORM models.
"""

from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel

from app.shared.enums import EditableComponentKind


class CreateEditableComponentDefinition(BaseModel):
    """Input contract for creating a new editable component definition.

    Responsibility:
    - Validate all required fields before the repository persists the record.
    """

    site_id: UUID
    solution_id: UUID
    key: str
    display_name: str
    description: Optional[str] = None
    kind: EditableComponentKind
    display_order: int = 0
    icon: Optional[str] = None
    editor_schema: list[dict[str, Any]] = []


class ListEditableComponentDefinitionQuery(BaseModel):
    """Query filter contract for listing editable component definitions.

    Responsibility:
    - Carry optional filter parameters from the service layer to the repository.
    """

    site_id: Optional[UUID] = None
    kind: Optional[EditableComponentKind] = None
