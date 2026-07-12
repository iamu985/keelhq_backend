"""Tests for RegistrationService.

Responsibility:
- Verify that RegistrationService orchestrates the registration use case,
  delegates to collaborators, and raises the correct domain errors.
"""

from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import SecretStr

from keelhq.core.unit_of_work import AbstractUnitOfWork
from keelhq.db.models import LocalUser
from keelhq.exceptions.identity import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
)
from keelhq.repositories.identity.local_user_repository import LocalUserRepository
from keelhq.schemas.identity.registration_schemas import (
    RegisterNewUserRequest,
    RegistrationSuccessfulResponse,
)
from keelhq.services.password_service import PasswordService
from keelhq.services.registration_service import RegistrationService


class FakeUnitOfWork(AbstractUnitOfWork):
    """In-memory Unit of Work for unit testing RegistrationService."""

    def __init__(self, users_repository: AsyncMock) -> None:
        self.users = cast(LocalUserRepository, users_repository)
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        return

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


@pytest.fixture
def mock_users_repository() -> AsyncMock:
    """Return a mocked LocalUserRepository with no existing users."""
    repo = AsyncMock(spec=LocalUserRepository)
    repo.get_by_username.return_value = None
    repo.get_by_email.return_value = None
    return repo


@pytest.fixture
def mock_password_service() -> MagicMock:
    """Return a mocked PasswordService that returns a deterministic hash."""
    service = MagicMock(spec=PasswordService)
    service.hash_password.return_value = "hashed_password"
    return service


@pytest.fixture
def uow(mock_users_repository: AsyncMock) -> FakeUnitOfWork:
    """Return a FakeUnitOfWork backed by the mocked user repository."""
    return FakeUnitOfWork(mock_users_repository)


@pytest.fixture
def registration_service(
    uow: FakeUnitOfWork,
    mock_password_service: MagicMock,
) -> RegistrationService:
    """Return a RegistrationService backed by the fake UoW and mocked services."""
    return RegistrationService(uow=uow, password_service=mock_password_service)


@pytest.fixture
def valid_request() -> RegisterNewUserRequest:
    """Return a fully valid registration request."""
    return RegisterNewUserRequest(
        username="valid_user",
        email="user@example.com",
        first_name="Frank",
        last_name="Castle",
        password=SecretStr("Secret123!"),
        password_confirm=SecretStr("Secret123!"),
    )


# TODO: add unit tests for database-level integrity error handling once relevant.
@pytest.mark.asyncio
async def test_register_success(
    registration_service: RegistrationService,
    uow: FakeUnitOfWork,
    mock_users_repository: AsyncMock,
    mock_password_service: MagicMock,
    valid_request: RegisterNewUserRequest,
) -> None:
    """A valid registration should persist the user, commit, and return a response."""
    result = await registration_service.register(valid_request)

    assert isinstance(result, RegistrationSuccessfulResponse)
    assert result.email == valid_request.email
    assert result.verification_required is True

    mock_password_service.hash_password.assert_called_once_with(valid_request.password)
    mock_users_repository.create.assert_awaited_once()
    assert uow.committed is True

    created_user = mock_users_repository.create.call_args[0][0]
    assert isinstance(created_user, LocalUser)
    assert created_user.username == valid_request.username
    assert created_user.email == str(valid_request.email)
    assert created_user.password_hash == "hashed_password"
    assert created_user.first_name == valid_request.first_name
    assert created_user.last_name == valid_request.last_name


@pytest.mark.asyncio
async def test_register_username_already_exists(
    registration_service: RegistrationService,
    uow: FakeUnitOfWork,
    mock_users_repository: AsyncMock,
    valid_request: RegisterNewUserRequest,
) -> None:
    """Duplicate usernames should raise UsernameAlreadyExistsError before persisting."""
    existing_user = MagicMock(spec=LocalUser)
    mock_users_repository.get_by_username.return_value = existing_user

    with pytest.raises(UsernameAlreadyExistsError):
        await registration_service.register(valid_request)

    mock_users_repository.get_by_email.assert_not_awaited()
    mock_users_repository.create.assert_not_awaited()
    assert uow.committed is False


@pytest.mark.asyncio
async def test_register_email_already_exists(
    registration_service: RegistrationService,
    uow: FakeUnitOfWork,
    mock_users_repository: AsyncMock,
    valid_request: RegisterNewUserRequest,
) -> None:
    """Duplicate emails should raise EmailAlreadyExistsError before persisting."""
    existing_user = MagicMock(spec=LocalUser)
    mock_users_repository.get_by_email.return_value = existing_user

    with pytest.raises(EmailAlreadyExistsError):
        await registration_service.register(valid_request)

    mock_users_repository.create.assert_not_awaited()
    assert uow.committed is False
