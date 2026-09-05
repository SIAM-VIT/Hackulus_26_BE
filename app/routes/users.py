from typing import Optional
from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.user import User
from app.models.participant_profile import ParticipantProfile
from app.models.submission import Submission
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionUpdate,
    Review0SubmissionCreate,
    Review1SubmissionCreate,
    Review2SubmissionCreate
)
from app.services.user_service import UserService
from app.services.submission_service import SubmissionService
from app.services.team_service import TeamService
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/home", summary="Get participant dashboard")
async def get_users_home(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await UserService.get_user_dashboard(db, current_user)

@router.get("/submissions", summary="List team submissions")
async def get_user_submissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pi = current_user.participant_profile
    if not pi or not pi.team_id:
        return {"submissions": []}

    res = await db.execute(
        select(Submission)
        .where(Submission.team_id == pi.team_id)
        .order_by(Submission.created_at.desc())
    )
    submissions = res.scalars().all()
    return {"submissions": submissions}

@router.post("/review0", status_code=status.HTTP_201_CREATED, summary="Review 0: Select and Lock Track & Final Problem Statement")
async def submit_review_0(
    data: Review0SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await SubmissionService.submit_review0(db, current_user, data)

@router.post("/review1", status_code=status.HTTP_201_CREATED, summary="Review 1: Submit GitHub & PPT links")
async def submit_review_1(
    data: Review1SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await SubmissionService.submit_review1(db, current_user, data)

@router.post("/review2", status_code=status.HTTP_201_CREATED, summary="Review 2 (Final): Submit Final GitHub, Deployed URL & PPT")
async def submit_review_2(
    data: Review2SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await SubmissionService.submit_review2(db, current_user, data)

@router.post("/submission/review", status_code=status.HTTP_201_CREATED, summary="Generic Review Submission")
async def create_user_submission(
    data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await SubmissionService.create_submission(db, current_user, data)

@router.put("/submission/{submission_id}", summary="Update existing submission")
async def update_user_submission(
    submission_id: int,
    data: SubmissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await SubmissionService.update_submission(db, submission_id, current_user, data)

@router.put("/team/problem-statement", summary="Update team problem statement")
async def update_user_team_problem_statement(
    problem_statement_id: int = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await TeamService.update_problem_statement(db, current_user, problem_statement_id)
