"""Registration routes.

Responsibility:
- Expose the user-registration use case as an HTTP endpoint.
"""

from fastapi import APIRouter, Depends

from keelhq.api.deps import get_registration_service
from keelhq.schemas.identity.registration_schemas import (
    RegisterNewUserRequest,
    RegistrationSuccessfulResponse,
)
from keelhq.services.registration_service import RegistrationService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegistrationSuccessfulResponse)
async def register(
    payload: RegisterNewUserRequest,
    service: RegistrationService = Depends(get_registration_service),
) -> RegistrationSuccessfulResponse:
    """Register a new local user."""
    return await service.register(payload)
