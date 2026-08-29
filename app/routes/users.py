from typing import Optional
from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.user import User
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionUpdate
from app.services.user_service import UserService
from app.services.submission_service import SubmissionService
from app.services.team_service import TeamService
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/home")
async def get_users_home(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await UserService.get_user_dashboard(db, current_user)

@router.get("/submissions")
async def get_user_submissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.team_id:
        return {"submissions": []}

    res = await db.execute(
        select(Submission)
        .where(Submission.team_id == current_user.team_id)
        .order_by(Submission.created_at.desc())
    )
    submissions = res.scalars().all()
    return {"submissions": submissions}

@router.post("/submission/review", status_code=status.HTTP_201_CREATED)
async def create_user_submission(
    data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await SubmissionService.create_submission(db, current_user, data)

@router.put("/submission/{submission_id}")
async def update_user_submission(
    submission_id: int,
    data: SubmissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await SubmissionService.update_submission(db, submission_id, current_user, data)

@router.put("/team/problem-statement")
async def update_user_team_problem_statement(
    problem_statement: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await TeamService.update_problem_statement(db, current_user, problem_statement)
