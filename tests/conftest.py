"""Shared pytest fixtures.

Responsibility:
- Provide reusable test fixtures for the test suite.
"""

import pytest
from fastapi import FastAPI

from keelhq.core.lifespan import lifespan


@pytest.fixture
def app() -> FastAPI:
    """Return a FastAPI application instance that uses the real lifespan."""
    return FastAPI(lifespan=lifespan)
