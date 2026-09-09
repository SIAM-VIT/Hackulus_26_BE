import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from sqlalchemy import select
from app.core.database import engine, Base, AsyncSessionLocal
import app.models  # Ensure all models are registered in Base.metadata
from app.models.event_config import EventConfig
from app.routes import auth, users, teams, submissions, reviews, admin, panels

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create all tables in PostgreSQL on startup
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created/verified successfully on startup.")

        # Ensure default EventConfig row exists
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(EventConfig).where(EventConfig.id == 1))
            config = res.scalar_one_or_none()
            if not config:
                config = EventConfig(id=1, current_phase="Participants reach", active_windows={"review0": False, "review1": False, "review2": False})
                session.add(config)
                await session.commit()
                print("✅ Default EventConfig row initialized.")
    except Exception as e:
        print(f"❌ Warning: Could not initialize database tables: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI Backend for Hackulus Hackathon Management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload dir exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(submissions.router)
app.include_router(reviews.router)
app.include_router(admin.router)
app.include_router(panels.router)

@app.get("/")
async def root():
    return {
        "message": "Hackulus 2026 FastAPI Backend is running!",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", summary="Health check / Keep-alive ping endpoint")
@app.get("/ping", summary="Health check / Keep-alive ping endpoint")
async def health_check():
    return {
        "status": "ok",
        "alive": True
    }
