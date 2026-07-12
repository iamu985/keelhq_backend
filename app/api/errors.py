"""Global exception-to-HTTP response mapping.

Responsibility:
- Convert KeelHQ domain exceptions into a consistent JSON error response.
- Provide a catch-all handler for unexpected errors.
"""

from typing import cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logger import logger
from app.exceptions import KeelException


async def keel_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a JSON error response for any KeelException."""
    error = cast(KeelException, exc)
    status_code = error.status_code
    body = {"error": {"code": error.error_code, "message": str(error)}}
    logger.warning(f"Domain error {error.error_code} -> {status_code}: {error}")
    return JSONResponse(status_code=status_code, content=body)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a generic 500 JSON response for unhandled exceptions."""
    logger.exception("Unhandled exception")
    body = {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
        }
    }
    return JSONResponse(status_code=500, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global exception handlers to the FastAPI application."""
    app.add_exception_handler(KeelException, keel_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
