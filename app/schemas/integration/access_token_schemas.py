"""Integration — AccessToken Pydantic schemas.

Responsibility:
- Define API contracts for creating and querying AccessToken resources.
- Keep schemas decoupled from ORM models.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateAccessToken(BaseModel):
    """Input contract for creating a new access token.

    Responsibility:
    - Validate all required fields before the repository persists the record.
    - Never expose the raw token; only the pre-hashed value is accepted here.
    """

    site_id: UUID
    name: str
    description: Optional[str] = None
    token_hash: str
    expires_at: Optional[datetime] = None
    is_active: bool = True


class ListAccessTokenQuery(BaseModel):
    """Query filter contract for listing access tokens.

    Responsibility:
    - Carry optional filter parameters from the service layer to the repository.
    """

    site_id: Optional[UUID] = None
    is_active: Optional[bool] = None
