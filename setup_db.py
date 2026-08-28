import asyncio
from app.core.database import engine, Base
import app.models  # Import all models so metadata discovers tables

async def init_db():
    print("Creating all database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
