"""Local user model for development-only authentication.

Responsibility:
- Define the database schema for local development user accounts.
"""

from sqlmodel import Field

from app.db.models.mixins import BaseModel


# TODO: add unit tests for this model
class LocalUser(BaseModel, table=True):
    """Development-only local user account.

    Responsibility:
    - Store local user identity and authentication details for development.
    """

    __tablename__ = "local_users"  # pyright: ignore

    email: str = Field(unique=True, index=True, nullable=False)
    username: str = Field(unique=True, index=True, nullable=False)
    password_hash: str = Field(nullable=False)
    first_name: str = Field(nullable=False)
    middle_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
