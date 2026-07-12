"""Tests for the registration route.

Responsibility:
- Verify the POST /auth/register endpoint delegates to RegistrationService
  and returns the expected response.
"""

from collections.abc import AsyncIterator
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine

from keelhq.api.deps import get_registration_service
from keelhq.api.v1.identity import router as identity_router
from keelhq.core.lifespan import lifespan
from keelhq.schemas.identity.registration_schemas import (
    RegistrationSuccessfulResponse,
)
from keelhq.services.registration_service import RegistrationService


@pytest.fixture
def app() -> FastAPI:
    """Return a FastAPI app with the identity router and real lifespan."""
    application = FastAPI(lifespan=lifespan)
    application.include_router(identity_router)
    return application


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """Yield an async HTTP client with lifespan started and a mocked engine."""
    mock_engine = MagicMock(spec=AsyncEngine)
    mock_engine.dispose = AsyncMock()

    with patch("keelhq.core.lifespan.create_engine", return_value=mock_engine):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as http_client:
            yield http_client


# TODO: add tests for validation errors and conflict responses.
@pytest.mark.asyncio
async def test_register_endpoint_returns_service_response(
    app: FastAPI,
    client: AsyncClient,
) -> None:
    """The register endpoint should return the response produced by RegistrationService."""
    expected_response = RegistrationSuccessfulResponse(
        message="User registered successfully.",
        email="user@example.com",
        verification_required=True,
    )

    mock_service = AsyncMock(spec=RegistrationService)
    mock_service.register.return_value = expected_response

    def fake_registration_service() -> RegistrationService:
        return cast(RegistrationService, mock_service)

    app.dependency_overrides[get_registration_service] = fake_registration_service

    response = await client.post(
        "/auth/register",
        json={
            "username": "valid_user",
            "email": "user@example.com",
            "first_name": "Frank",
            "last_name": "Castle",
            "password": "Secret123!",
            "password_confirm": "Secret123!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == expected_response.message
    assert data["email"] == expected_response.email
    assert data["verification_required"] is True
    mock_service.register.assert_awaited_once()
