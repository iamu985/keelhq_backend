from typing import List, Optional
from pydantic import BaseModel, EmailStr, UUID4


class CreateLocalUser(BaseModel):
    email: EmailStr
    username: str
    password_hash: UUID4
    first_name: str
    middle_name: Optional[str]
    last_name: Optional[str]


class LocalUserDetail(BaseModel):
    id: UUID4
    email: EmailStr
    username: str
    first_name: str
    middle_name: Optional[str]
    last_name: Optional[str]
    created_at: str
    is_active: bool = False
    is_superuser: bool = False


class ListLocalUser(BaseModel):
    local_users: List["LocalUserDetail"]
