from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings, T_Environment


def get_connection_string():
    username = settings.database.username
    password = settings.database.password.get_secret_value()
    host = settings.database.host
    port = settings.database.port
    database = settings.database.database

    return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"


def create_engine():
    echo = False
    match settings.environment:
        case T_Environment.PRODUCTION:
            echo = False
        case T_Environment.DEVELOPMENT:
            echo = True

    return create_async_engine(url=get_connection_string(), echo=echo, future=True)


ENGINE = create_engine()
