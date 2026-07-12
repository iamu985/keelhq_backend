"""
Responsibility:
    Any models that are a combination of different schemas from other domains.
    Will be defined here.
"""

from uuid import UUID

from pydantic import BaseModel

from app.schemas.content_engine import (
    CreateContentEntry,
    CreateEditableComponentDefinition,
)
from app.schemas.forms import CreateForm
from app.schemas.media import CreateMediaAsset
from app.schemas.site_management import CreateSolution
from app.shared.enums import SiteStatus, SiteVisibility


class SiteDetail(BaseModel):
    owner_id: UUID
    name: str
    slug: str
    description: str | None = None
    logo_url: str | None = None
    status: SiteStatus
    visibility: SiteVisibility
    extension_id: CreateSolution

    definitions: list[CreateEditableComponentDefinition] = []
    content_entries: list[CreateContentEntry] = []
    media_assets: list[CreateMediaAsset] = []
    forms: list[CreateForm] = []
