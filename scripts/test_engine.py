import asyncio
from sqlalchemy import text
from app.db.engine import ENGINE


async def test_connection():
    async with ENGINE.connect() as conn:
        print("✅ Connection acquired.")

        result = await conn.execute(text("Select 1"))

        row = result.fetchone()

        if not row:
            print("No row.")
            return

        print("🗒️ Query result:", row[0])

        await ENGINE.dispose()
        print("🔌 Connection closed")


if __name__ == "__main__":
    asyncio.run(test_connection())
