"""Tests for the FastAPI lifespan context manager.

Responsibility:
- Verify startup creates engine, session factory, and stateless services on
  app.state, and shutdown disposes the engine.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.core.lifespan import lifespan
from app.services.password_service import PasswordService


# TODO: add unit tests for error handling during startup/shutdown once relevant.
@pytest.mark.asyncio
async def test_lifespan_initializes_and_disposes_engine() -> None:
    """Startup creates resources on app.state; shutdown disposes the engine."""
    mock_engine = MagicMock(spec=AsyncEngine)
    mock_engine.dispose = AsyncMock()

    app = FastAPI(lifespan=lifespan)

    with patch("app.core.lifespan.create_engine", return_value=mock_engine):
        with TestClient(app):
            assert app.state.engine is mock_engine
            assert isinstance(app.state.session_factory, async_sessionmaker)
            assert isinstance(app.state.password_service, PasswordService)

    mock_engine.dispose.assert_awaited_once()
