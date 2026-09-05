import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import auth, users, teams, submissions, reviews, admin, panels

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI Backend for Hackulus Hackathon Management",
    version="1.0.0"
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
