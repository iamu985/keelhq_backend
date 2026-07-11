"""Site Management — Site Pydantic schemas.

Responsibility:
- Define API contracts for creating and querying Site resources.
- Keep schemas decoupled from ORM models.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from app.shared.enums import SiteStatus, SiteVisibility


class CreateSite(BaseModel):
    """Input contract for creating a new site.

    Responsibility:
    - Validate all required fields before the repository persists the record.
    """

    owner_id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    status: SiteStatus
    visibility: SiteVisibility
    extension_id: Optional[UUID] = None


class SiteResponse(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    status: SiteStatus
    visibility: SiteVisibility


class ListSiteQuery(BaseModel):
    """Query filter contract for listing sites.

    Responsibility:
    - Carry optional filter parameters from the service layer to the repository.
    """

    owner_id: Optional[UUID] = None
    status: Optional[SiteStatus] = None
    visibility: Optional[SiteVisibility] = None
