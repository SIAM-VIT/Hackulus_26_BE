import asyncio
from app.core.database import engine, Base
import app.models  # Import all models so metadata discovers tables

from sqlalchemy import text

async def init_db():
    print("Recreating clean database schema...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
