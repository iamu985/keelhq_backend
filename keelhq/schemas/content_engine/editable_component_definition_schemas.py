"""Content Engine — EditableComponentDefinition Pydantic schemas.

Responsibility:
- Define API contracts for creating and querying EditableComponentDefinition resources.
- Keep schemas decoupled from ORM models.
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel

from keelhq.shared.enums import EditableComponentKind


class CreateEditableComponentDefinition(BaseModel):
    """Input contract for creating a new editable component definition.

    Responsibility:
    - Validate all required fields before the repository persists the record.
    """

    site_id: UUID
    solution_id: UUID
    key: str
    display_name: str
    description: str | None = None
    kind: EditableComponentKind
    display_order: int = 0
    icon: str | None = None
    editor_schema: list[dict[str, Any]] = []


class ListEditableComponentDefinitionQuery(BaseModel):
    """Query filter contract for listing editable component definitions.

    Responsibility:
    - Carry optional filter parameters from the service layer to the repository.
    """

    site_id: UUID | None = None
    kind: EditableComponentKind | None = None
