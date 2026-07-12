"""Alembic migration environment.

Responsibility:
- Configure Alembic for async SQLAlchemy 2.x migrations.
- Load the database URL from application settings.
- Use the project's existing AsyncEngine for online migrations.
"""

import asyncio
from logging.config import fileConfig
from typing import Any, Literal

from alembic import context
from sqlalchemy.engine import Connection

# keelhq imports
from keelhq.core.config import settings
from keelhq.db.base import metadata
from keelhq.db.engine import create_engine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Load the database URL from application settings instead of alembic.ini.
# This is required for offline mode and keeps the single source of truth.
config.set_main_option("sqlalchemy.url", settings.database.connection_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def render_item(type_: str, obj: Any, autogen_context: Any) -> str | Literal[False]:
    """Render SQLModel AutoString as plain SQLAlchemy sa.String.

    SQLModel's AutoString is a String subclass. Rendering it as sa.String
    avoids generated migrations importing sqlmodel internals, which would cause
    NameError if the migration template does not import sqlmodel.
    """
    if type_ == "type" and type(obj).__name__ == "AutoString":
        length = getattr(obj, "length", None)
        if length:
            return f"sa.String(length={length})"
        return "sa.String()"
    return False


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Synchronous callback executed inside the async connection.

    context.configure must happen here because connection.run_sync provides
    a synchronous Connection proxy, and Alembic's context expects a sync
    connection.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_item=render_item,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using a freshly created AsyncEngine."""
    engine = create_engine()
    try:
        async with engine.connect() as connection:
            await connection.run_sync(do_run_migrations)
    finally:
        await engine.dispose()


async def main() -> None:
    """Entry point that selects offline or online migration mode."""
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        await run_migrations_online()


asyncio.run(main())
