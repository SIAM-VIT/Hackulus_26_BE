from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.schemas.review import ReviewCreateUpdate
from app.services.review_service import ReviewService
from app.dependencies import get_current_judge_or_admin

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/submission/{submission_id}")
async def submit_review(
    submission_id: int,
    data: ReviewCreateUpdate,
    db: AsyncSession = Depends(get_db),
    current_judge: User = Depends(get_current_judge_or_admin)
):
    return await ReviewService.create_or_update_review(db, submission_id, current_judge, data)
