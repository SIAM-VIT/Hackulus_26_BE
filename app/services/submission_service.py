import os
from typing import Optional
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.submission import Submission, SubmissionType, SubmissionStatus
from app.models.team import Team, TeamStatus
from app.models.user import User
from app.models.event_config import EventConfig
from app.schemas.submission import SubmissionCreate, SubmissionUpdate
from app.core.config import settings

class SubmissionService:
    @staticmethod
    async def create_submission(
        db: AsyncSession,
        user: User,
        data: SubmissionCreate,
        file: Optional[UploadFile] = None
    ):
        if not user.team_id:
            raise HTTPException(status_code=400, detail="User must belong to a team")
        if not user.is_leader:
            raise HTTPException(status_code=403, detail="Only the team leader can submit")

        # Check Team Status
        team = await db.get(Team, user.team_id)
        if team and team.status == TeamStatus.REJECTED:
            raise HTTPException(status_code=403, detail="Team is eliminated")

        # Check Submission Window
        config_res = await db.execute(select(EventConfig).where(EventConfig.id == 1))
        config = config_res.scalar_one_or_none()
        windows = config.active_windows if config else {}

        if not windows.get(data.type, False):
            raise HTTPException(status_code=403, detail=f"{data.type} submissions are closed")

        # Handle File Upload
        file_path_url = None
        if file:
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            file_name = f"{user.team_id}_{file.filename}"
            full_path = os.path.join(settings.UPLOAD_DIR, file_name)
            contents = await file.read()
            with open(full_path, "wb") as f:
                f.write(contents)
            file_path_url = f"/uploads/{file_name}"

        links_data = data.links or {}
        if file_path_url:
            links_data["file"] = file_path_url

        submission = Submission(
            team_id=user.team_id,
            submitted_by=user.user_id,
            type=SubmissionType(data.type),
            title=data.title,
            description=data.description,
            links=links_data,
            status=SubmissionStatus.SUBMITTED
        )

        db.add(submission)
        await db.commit()
        await db.refresh(submission)
        return submission

    @staticmethod
    async def update_submission(
        db: AsyncSession,
        submission_id: int,
        user: User,
        data: SubmissionUpdate,
        file: Optional[UploadFile] = None
    ):
        submission = await db.get(Submission, submission_id)
        if not submission or submission.team_id != user.team_id:
            raise HTTPException(status_code=404, detail="Submission not found or unauthorized")

        if not user.is_leader:
            raise HTTPException(status_code=403, detail="Only team leader can modify submission")

        if data.title:
            submission.title = data.title
        if data.description:
            submission.description = data.description

        links_data = submission.links or {}
        if data.links:
            links_data.update(data.links)

        if file:
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            file_name = f"{user.team_id}_{file.filename}"
            full_path = os.path.join(settings.UPLOAD_DIR, file_name)
            contents = await file.read()
            with open(full_path, "wb") as f:
                f.write(contents)
            links_data["file"] = f"/uploads/{file_name}"

        submission.links = links_data
        await db.commit()
        await db.refresh(submission)
        return submission
