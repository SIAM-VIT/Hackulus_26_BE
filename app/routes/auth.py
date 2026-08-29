from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/user/signup", 
    response_model=TokenResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Self-Registration (Utility/Internal)",
    description=(
        "Registers an individual user. Note: In the standard managed hackathon workflow, "
        "participant accounts, teams, tracks, and problem statements are pre-provisioned "
        "by Admins via `POST /admin/team/create-with-members`. This endpoint remains for "
        "testing, utility, or standalone user onboarding."
    )
)
async def user_signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.signup_user(db, data)

@router.post(
    "/user/login", 
    response_model=TokenResponse,
    summary="User Login",
    description="Authenticates participants, judges, or admins and returns JWT bearer token with user details."
)
async def user_login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.login_user(db, data)

from app.schemas.user import UserResponse
from app.dependencies import get_current_user
from app.models.user import User

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get authenticated user info"
)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
