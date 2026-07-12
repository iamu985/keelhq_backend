from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from keelhq.core.config import T_Environment, settings


def create_engine() -> AsyncEngine:
    echo = False
    match settings.environment:
        case T_Environment.PRODUCTION:
            echo = False
        case T_Environment.DEVELOPMENT:
            echo = True

    return create_async_engine(url=settings.database.connection_url, echo=echo, future=True)
