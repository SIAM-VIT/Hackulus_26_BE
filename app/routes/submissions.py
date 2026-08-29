from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.user import User
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionUpdate
from app.services.submission_service import SubmissionService
from app.dependencies import get_current_user

router = APIRouter(prefix="/submissions", tags=["Submissions"])

@router.get("/")
async def list_my_submissions(
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

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_submission(
    data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await SubmissionService.create_submission(db, current_user, data)

@router.put("/{submission_id}")
async def update_submission(
    submission_id: int,
    data: SubmissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await SubmissionService.update_submission(db, submission_id, current_user, data)
