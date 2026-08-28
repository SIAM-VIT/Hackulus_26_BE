from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/user/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def user_signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.signup_user(db, data)

@router.post("/user/login", response_model=TokenResponse)
async def user_login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.login_user(db, data)
