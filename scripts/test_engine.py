"""Manual database connectivity script.

Responsibility:
- Provide a quick way to verify the async database engine can connect and execute.
"""

import asyncio

import pytest
from sqlalchemy import text

from app.db.engine import create_engine


@pytest.mark.asyncio
async def test_connection() -> None:
    engine = create_engine()
    async with engine.connect() as conn:
        print("✅ Connection acquired.")

        result = await conn.execute(text("Select 1"))

        row = result.fetchone()

        if not row:
            print("No row.")
            return

        print("🗒️ Query result:", row[0])

        await engine.dispose()
        print("🔌 Connection closed")


if __name__ == "__main__":
    asyncio.run(test_connection())
