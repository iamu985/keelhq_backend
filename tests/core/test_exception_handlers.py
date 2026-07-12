"""Tests for global exception handlers.

Responsibility:
- Verify KeelException and unhandled Exception mappings produce the expected JSON
  responses and status codes.
"""

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

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
