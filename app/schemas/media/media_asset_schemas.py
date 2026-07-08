"""Media — MediaAsset Pydantic schemas.

Responsibility:
- Define API contracts for creating and querying MediaAsset resources.
- Keep schemas decoupled from ORM models and storage provider details.
"""

from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class CreateMediaAsset(BaseModel):
    """Input contract for creating a new media asset.

    Responsibility:
    - Validate all required fields before the repository persists the record.
    - The actual file bytes are stored by the caller in an external provider
      before this schema is used; only the resulting metadata is captured here.
    """

    site_id: UUID
    filename: str
    storage_key: str
    mime_type: Optional[str] = None
    extension: Optional[str] = None
    size: int
    width: Optional[int] = None
    height: Optional[int] = None
    alt_text: Optional[str] = None
    extra_metadata: dict[str, Any] = {}


class ListMediaAssetQuery(BaseModel):
    """Query filter contract for listing media assets.

    Responsibility:
    - Carry optional filter parameters from the service layer to the repository.
    """

    site_id: Optional[UUID] = None
    mime_type: Optional[str] = None
    extension: Optional[str] = None
