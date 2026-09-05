from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.schemas.review import ReviewCreateUpdate
from app.services.review_service import ReviewService
from app.dependencies import get_current_user, get_current_judge_or_admin

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/submission/{submission_id}", summary="Judge/Admin: Evaluate submission across 6 categories")
async def submit_review(
    submission_id: int,
    data: ReviewCreateUpdate,
    db: AsyncSession = Depends(get_db),
    current_judge: User = Depends(get_current_judge_or_admin)
):
    """
    Evaluates a submission across the 6 categories:
    1. Innovation & Originality (innovation_score)
    2. Technical Complexity & Architecture (technical_complexity_score)
    3. Feasibility & Practicality (feasibility_score)
    4. UI/UX & Design (ui_ux_score)
    5. Presentation & Pitch (presentation_score)
    6. Progress & Execution (progress_score)
    """
    return await ReviewService.create_or_update_review(db, submission_id, current_judge, data)

@router.get("/team/{team_id}", summary="Get evaluation scorecard for a team")
async def get_team_reviews(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await ReviewService.get_team_reviews(db, team_id)

@router.get("/leaderboard", summary="Get hackathon scores & rankings")
async def get_leaderboard(
    round_name: Optional[str] = Query(None, description="Optional filter by round: review1 or review2"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await ReviewService.get_leaderboard(db, round_name)
