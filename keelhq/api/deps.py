"""FastAPI dependencies.

Responsibility:
- Provide request-scoped and application-scoped objects for API routes.
"""

from collections.abc import AsyncGenerator
from typing import Any, cast

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import async_sessionmaker

from keelhq.core.unit_of_work import AbstractUnitOfWork
from keelhq.db.unit_of_work import SqlAlchemyUnitOfWork
from keelhq.services.local_user_service import LocalUserService
from keelhq.services.password_service import PasswordService
from keelhq.services.registration_service import RegistrationService


async def get_uow(request: Request) -> AsyncGenerator[AbstractUnitOfWork, None]:
    """Yield a request-scoped SQLAlchemy Unit of Work."""
    session_factory = cast(async_sessionmaker[Any], request.app.state.session_factory)
    async with SqlAlchemyUnitOfWork(session_factory) as uow:
        yield uow


def get_password_service(request: Request) -> PasswordService:
    """Return the application-scoped PasswordService."""
    return cast(PasswordService, request.app.state.password_service)


def get_registration_service(
    uow: AbstractUnitOfWork = Depends(get_uow),
    password_service: PasswordService = Depends(get_password_service),
) -> RegistrationService:
    """Return a RegistrationService backed by the request UoW and password service."""
    return RegistrationService(uow=uow, password_service=password_service)


def get_local_user_service(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> LocalUserService:
    """Return a LocalUserService backed by the request UoW."""
    return LocalUserService(uow=uow)
