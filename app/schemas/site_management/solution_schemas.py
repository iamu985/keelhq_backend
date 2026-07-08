"""Site Management — Solution Pydantic schemas.

Responsibility:
- Define API contracts for creating and querying Solution resources.
- Keep schemas decoupled from ORM models.
"""

from typing import Optional

from pydantic import BaseModel


class CreateSolution(BaseModel):
    """Input contract for creating a new solution.

    Responsibility:
    - Validate all required fields before the repository persists the record.
    """

    name: str
    slug: str
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    version: str = "0.1.0"
    is_builtin: bool = True


class ListSolutionQuery(BaseModel):
    """Query filter contract for listing solutions.

    Responsibility:
    - Carry optional filter parameters from the service layer to the repository.
    """

    is_builtin: Optional[bool] = None
