"""FastAPI lifespan context manager.

Responsibility:
- Own startup and shutdown of application-scoped resources:
  database engine, session factory, and stateless services.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.logger import logger
from app.db.engine import create_engine
from app.db.session import create_session_factory
from app.services.password_service import PasswordService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage the application lifecycle."""
    logger.info("KeelHQ starting up")

    engine: AsyncEngine = create_engine()
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)

    # Application-scoped stateless services.
    app.state.password_service = PasswordService()
    # TODO: initialize TokenService, EmailService, Redis, queues, etc.

    logger.info("KeelHQ startup complete")

    yield

    logger.info("KeelHQ shutting down")

    # TODO: teardown TokenService, EmailService, Redis, queues, etc.

    await engine.dispose()

    logger.info("KeelHQ shutdown complete")
