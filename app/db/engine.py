from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings, T_Environment


def create_engine():
    echo = False
    match settings.environment:
        case T_Environment.PRODUCTION:
            echo = False
        case T_Environment.DEVELOPMENT:
            echo = True

    return create_async_engine(
        url=settings.database.connection_url, echo=echo, future=True
    )


ENGINE = create_engine()
