"""Global exception-to-HTTP response mapping.

Responsibility:
- Convert KeelHQ domain exceptions into a consistent JSON error response.
- Provide a catch-all handler for unexpected errors.
"""

from collections.abc import Sequence
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from keelhq.core.logger import logger
from keelhq.exceptions import KeelException


def _format_validation_message(errors: Sequence[Any]) -> str:
    """Build a readable message from Pydantic validation errors."""
    messages = []
    for error in errors:
        loc = " -> ".join(str(part) for part in error.get("loc", []))
        msg = error.get("msg", "Invalid value")
        messages.append(f"{loc}: {msg}")
    return "; ".join(messages) if messages else "Invalid request."


def _code_for_http_status(status_code: int) -> str:
    """Return a stable error code for common HTTP status codes."""
    mapping = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
    }
    return mapping.get(status_code, f"HTTP_{status_code}")


async def request_validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a 422 JSON response for Pydantic/FastAPI validation errors."""
    validation_exc = cast(RequestValidationError, exc)
    body = {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": _format_validation_message(validation_exc.errors()),
        }
    }
    return JSONResponse(status_code=422, content=body)


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a JSON response for FastAPI HTTPException."""
    http_exc = cast(HTTPException, exc)
    body = {
        "error": {
            "code": _code_for_http_status(http_exc.status_code),
            "message": str(http_exc.detail),
        }
    }
    return JSONResponse(status_code=http_exc.status_code, content=body)


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
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(KeelException, keel_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
