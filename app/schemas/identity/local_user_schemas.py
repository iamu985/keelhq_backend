"""Identity domain Pydantic schemas.

Responsibility:
- Define API contracts for creating and reading LocalUser resources.
- Keep schemas free of database or ORM imports.
"""

from uuid import UUID

from pydantic import BaseModel, EmailStr


class CreateLocalUser(BaseModel):
    """Input contract for creating a new local user.

    Responsibility:
    - Validate all required fields before the repository persists the record.
    """

    email: EmailStr
    username: str
    password_hash: str
    first_name: str
    middle_name: str | None = None
    last_name: str | None = None


class LocalUserDetail(BaseModel):
    """Read representation of a local user.

    Responsibility:
    - Carry user data across service and presentation boundaries without
      exposing sensitive fields such as password_hash.
    """

    id: UUID
    email: EmailStr
    username: str
    first_name: str
    middle_name: str | None = None
    last_name: str | None = None
    created_at: str
    is_active: bool = False
    is_superuser: bool = False
