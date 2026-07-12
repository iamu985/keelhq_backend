"""SQLAlchemy-backed Unit of Work implementation.

Responsibility:
- Manage a single AsyncSession lifecycle.
- Construct repositories that share the session and transaction.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.unit_of_work import AbstractUnitOfWork
from app.db.session import SessionLocal
from app.repositories.identity.local_user_repository import LocalUserRepository


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """Concrete Unit of Work backed by an async SQLAlchemy session."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] = SessionLocal,
    ) -> None:
        self.session_factory = session_factory
        self._session: AsyncSession | None = None
        self.users: LocalUserRepository

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self.session_factory()
        self.users = LocalUserRepository(session=self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        if self._session is not None:
            if exc_type is not None:
                await self._session.rollback()
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        """Commit the current transaction."""
        if self._session is None:
            raise RuntimeError("Unit of work has not been entered")
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        if self._session is not None:
            await self._session.rollback()

    @property
    def session(self) -> AsyncSession:
        """Return the active session or raise if not entered."""
        if self._session is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._session
