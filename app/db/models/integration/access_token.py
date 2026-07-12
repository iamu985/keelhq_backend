"""Access token model.

Responsibility:
- Define the database schema for API/MCP access tokens that belong to a site.

An AccessToken allows AI coding agents and external tools to authenticate against a
site's content. The raw token is never stored; only a hash is persisted so that a
compromise of the database does not expose usable credentials.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship

from app.db.models.mixins import BaseModel, IsPartOfSite

if TYPE_CHECKING:
    from app.db.models.site_management.site import Site


# TODO: add unit tests for this model
class AccessToken(BaseModel, IsPartOfSite, table=True):
    """A secure API/MCP access token scoped to a site.

    Responsibility:
    - Store only the token hash, never the raw token.
    - Track usage and expiration for security auditing.
    """

    __tablename__ = "access_tokens"  # pyright: ignore

    name: str = Field(
        nullable=False,
        description="Human-readable label for the token (e.g., 'Claude Code').",
    )
    description: str | None = Field(
        default=None,
        description="Optional explanation of the token's purpose.",
    )
    token_hash: str = Field(
        nullable=False,
        unique=True,
        index=True,
        description="Hash of the raw token. The raw token is never persisted.",
    )
    last_used_at: datetime | None = Field(
        default=None,
        description="Most recent time the token was used to authenticate.",
    )
    expires_at: datetime | None = Field(
        default=None,
        description="Optional expiration time after which the token is rejected.",
    )
    is_active: bool = Field(
        default=True,
        nullable=False,
        description="Whether the token is currently allowed to authenticate.",
    )

    # Relationship.
    # Every token belongs to exactly one site.
    site: "Site" = Relationship(back_populates="access_tokens")

    __table_args__ = (  # pyright: ignore
        UniqueConstraint("token_hash", name="uq_access_tokens_token_hash"),
        Index("ix_access_tokens_site_id", "site_id"),
    )
