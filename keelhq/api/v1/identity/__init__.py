from fastapi import APIRouter

from .local_user_routes import router as local_user_router
from .registration_routes import router as registration_router

router = APIRouter()
router.include_router(local_user_router)
router.include_router(registration_router)

__all__ = ["router"]
