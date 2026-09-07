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
    Evaluates a submission across the 6 categories (Total 100%):
    1. Concept & Originality: 20% (innovation_score, 0-20)
    2. Technical Implementation & Complexity: 25% (technical_complexity_score, 0-25)
    3. Completion & Functionality: 20% (progress_score, 0-20)
    4. Real-World Impact & Viability: 15% (feasibility_score, 0-15)
    5. Design & User Experience (UX): 10% (ui_ux_score, 0-10)
    6. Team Contribution & Collaboration: 10% (presentation_score, 0-10)
    """
    return await ReviewService.create_or_update_review(db, submission_id, current_judge, data)

@router.get("/team/{team_id}", summary="Get evaluation scorecard for a team")
async def get_team_reviews(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await ReviewService.get_team_reviews(db, team_id)

@router.get("/leaderboard", summary="Judge/Admin: Get hackathon scores & rankings")
async def get_leaderboard(
    round_name: Optional[str] = Query(None, description="Optional filter by round: review1 or review2"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_judge_or_admin)
):
    return await ReviewService.get_leaderboard(db, round_name)
