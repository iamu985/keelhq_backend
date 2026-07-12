from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.engine import ENGINE

#  Create application session factory
SessionLocal = async_sessionmaker(
    bind=ENGINE,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
