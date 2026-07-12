from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends

from keelhq.api.deps import get_local_user_service
from keelhq.schemas.identity import CreateLocalUser, LocalUserDetail
from keelhq.services.local_user_service import LocalUserService

router = APIRouter(prefix="/local-user")


@router.post("/create")
async def create_local_user(
    payload: CreateLocalUser,
    service: LocalUserService = Depends(get_local_user_service),
) -> LocalUserDetail | dict[str, Any]:
    """Create a new local user."""
    result = await service.create(payload)
    if result is None:
        return {}
    return result


@router.get("/list")
async def list_local_users(
    service: LocalUserService = Depends(get_local_user_service),
) -> list[LocalUserDetail]:
    """List all local users."""
    return await service.list()


@router.get("/{user_id}/detail")
async def get_user_detail_by_id(
    user_id: str,
    service: LocalUserService = Depends(get_local_user_service),
) -> LocalUserDetail | dict[str, Any]:
    """Return details for a single local user."""
    result = await service.get_by_id(UUID(user_id))
    if result is None:
        return {}
    return result
