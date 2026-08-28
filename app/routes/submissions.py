from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json
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
    type: str = Form(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    links: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    parsed_links = json.loads(links) if links else None
    data = SubmissionCreate(
        type=type,
        title=title,
        description=description,
        links=parsed_links
    )
    return await SubmissionService.create_submission(db, current_user, data, file)

@router.put("/{submission_id}")
async def update_submission(
    submission_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    links: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    parsed_links = json.loads(links) if links else None
    data = SubmissionUpdate(
        title=title,
        description=description,
        links=parsed_links
    )
    return await SubmissionService.update_submission(db, submission_id, current_user, data, file)
