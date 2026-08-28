from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.services.user_service import UserService
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/home")
async def get_users_home(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await UserService.get_user_dashboard(db, current_user)
