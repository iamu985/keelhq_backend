"""Registration use-case service.

Responsibility:
- Orchestrate the new-user registration workflow.
- Enforce business rules (username/email uniqueness) and delegate hashing,
  persistence, and transaction control to collaborators.
"""

from app.core.logger import logger
from app.core.unit_of_work import AbstractUnitOfWork
from app.db.models import LocalUser
from app.exceptions.identity import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
)
from app.schemas.identity.registration_schemas import (
    RegisterNewUserRequest,
    RegistrationSuccessfulResponse,
)
from app.services.password_service import PasswordService


class RegistrationService:
    """Application service for registering new local users.

    Attributes:
        uow: Transaction boundary and repository access.
        password_service: Password hashing collaborator.
    """

    def __init__(
        self,
        uow: AbstractUnitOfWork,
        password_service: PasswordService,
    ) -> None:
        self.uow = uow
        self.password_service = password_service

    async def register(
        self,
        request: RegisterNewUserRequest,
    ) -> RegistrationSuccessfulResponse:
        """Register a new user after validating availability rules.

        Args:
            request: Validated registration payload.

        Returns:
            RegistrationSuccessfulResponse: Confirmation payload for the frontend.

        Raises:
            UsernameAlreadyExistsError: If the requested username is taken.
            EmailAlreadyExistsError: If the requested email is already registered.
        """
        logger.info(f"Starting registration for username={request.username}")

        existing_username = await self.uow.users.get_by_username(request.username)
        if existing_username is not None:
            logger.warning(f"Username already exists: {request.username}")
            raise UsernameAlreadyExistsError(f"Username '{request.username}' is already taken.")

        existing_email = await self.uow.users.get_by_email(str(request.email))
        if existing_email is not None:
            logger.warning(f"Email already registered: {request.email}")
            raise EmailAlreadyExistsError(f"Email '{request.email}' is already registered.")

        password_hash = self.password_service.hash_password(request.password)

        user = LocalUser(
            username=request.username,
            email=str(request.email),
            password_hash=password_hash,
            first_name=request.first_name,
            middle_name=None,
            last_name=request.last_name,
        )

        await self.uow.users.create(user)
        await self.uow.commit()

        logger.info(f"User registered successfully: username={request.username}")

        return RegistrationSuccessfulResponse(
            message="User registered successfully.",
            email=request.email,
            verification_required=True,
        )
