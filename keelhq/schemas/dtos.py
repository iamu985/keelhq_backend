from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class DLocalUser(BaseModel):
    """Domain level LocalUser schema"""

    id: UUID
    email: EmailStr
    username: str
    first_name: str
    middle_name: str
    last_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class DVerificationCode(BaseModel):
    """DTO Verification Code"""

    code: int = Field(max_length=6, min_length=6)
    expires_at: datetime
    is_used: bool
    local_user_id: UUID
