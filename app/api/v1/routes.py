import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> JSONResponse:
    response = settings.model_dump_json()
    # password: SecretStr = response["database"]["password"]
    # response["database"]["password"] = password.get_secret_value()
    config = json.loads(response)
    return JSONResponse(status_code=200, content=config)
