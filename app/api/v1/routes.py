from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import SecretStr

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    response = settings.model_dump()
    password: SecretStr = response["database"]["password"]
    response["database"]["password"] = password.get_secret_value()
    return JSONResponse(status_code=200, content=response)
