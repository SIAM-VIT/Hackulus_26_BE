import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Hackulus 2026 FastAPI Backend"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/hackulus"
    SECRET_KEY: str = "dev_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    UPLOAD_DIR: str = "uploads"
    SENTRY_DSN: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
