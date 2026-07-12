"""Unit of Work abstraction.

Responsibility:
- Define the transaction boundary and repository access contract.
- Concrete implementations own the session lifecycle.
"""

from abc import ABC, abstractmethod
from typing import Any

from keelhq.repositories.identity.local_user_repository import LocalUserRepository


class AbstractUnitOfWork(ABC):
    """Transaction boundary for application use cases.

    Responsibility:
    - Expose repositories that share a single transaction.
    - Provide commit/rollback control to application services.
    """

    users: LocalUserRepository

    @abstractmethod
    async def __aenter__(self) -> "AbstractUnitOfWork":
        """Enter the asynchronous transaction context."""
        ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        """Exit the asynchronous transaction context."""
        ...

    @abstractmethod
    async def commit(self) -> None:
        """Persist all changes made within the transaction."""
        ...

    @abstractmethod
    async def rollback(self) -> None:
        """Discard all changes made within the transaction."""
        ...
