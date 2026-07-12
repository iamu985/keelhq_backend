"""Tests for global exception handlers.

Responsibility:
- Verify KeelException and unhandled Exception mappings produce the expected JSON
  responses and status codes.
"""

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, field_validator

from app.api.errors import register_exception_handlers
from app.exceptions import DomainError
from app.exceptions.identity import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
)

router = APIRouter()


@router.get("/username-taken")
async def username_taken() -> None:
    raise UsernameAlreadyExistsError("Username 'frank' is already taken.")


@router.get("/email-taken")
async def email_taken() -> None:
    raise EmailAlreadyExistsError("Email 'frank@example.com' is already registered.")


@router.get("/domain-error")
async def domain_error() -> None:
    raise DomainError("Something went wrong.")


@router.get("/unhandled")
async def unhandled() -> None:
    raise RuntimeError("boom")


class SamplePayload(BaseModel):
    """Minimal model that enforces a validation rule for handler tests."""

    password: str

    @field_validator("password")
    @classmethod
    def require_uppercase(cls, value: str) -> str:
        if not any(char.isupper() for char in value):
            raise ValueError("password must contain at least one uppercase letter")
        return value


@router.post("/validate")
async def validate(payload: SamplePayload) -> None:
    return None


@router.get("/not-found")
async def not_found() -> None:
    raise HTTPException(status_code=404, detail="Resource not found")


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    register_exception_handlers(app)
    return TestClient(app, raise_server_exceptions=False)


def test_username_already_exists_error() -> None:
    """UsernameAlreadyExistsError maps to 409 with the correct error code."""
    client = _client()
    response = client.get("/username-taken")

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "USERNAME_ALREADY_EXISTS",
            "message": "Username 'frank' is already taken.",
        }
    }


def test_email_already_exists_error() -> None:
    """EmailAlreadyExistsError maps to 409 with the correct error code."""
    client = _client()
    response = client.get("/email-taken")

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "EMAIL_ALREADY_EXISTS",
            "message": "Email 'frank@example.com' is already registered.",
        }
    }


def test_unmapped_domain_error() -> None:
    """Unmapped DomainError subclasses fall back to 400 Bad Request."""
    client = _client()
    response = client.get("/domain-error")

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "DOMAIN_ERROR",
            "message": "Something went wrong.",
        }
    }


def test_unhandled_exception_returns_500() -> None:
    """Unhandled non-Keel exceptions return a generic 500 JSON response."""
    client = _client()
    response = client.get("/unhandled")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
        }
    }


def test_request_validation_error_returns_422() -> None:
    """Pydantic validation errors map to 422 with a VALIDATION_ERROR code."""
    client = _client()
    response = client.post("/validate", json={"password": "abcd.1234"})

    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "password must contain at least one uppercase letter" in data["error"]["message"]


def test_http_exception_returns_mapped_code() -> None:
    """FastAPI HTTPException maps to the unified format with the matching status code."""
    client = _client()
    response = client.get("/not-found")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "NOT_FOUND",
            "message": "Resource not found",
        }
    }
