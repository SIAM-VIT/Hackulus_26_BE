from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models.submission import Submission
from app.models.team import Team
from app.models.review import Review
from app.models.user import User, UserRole
from app.schemas.review import ReviewCreateUpdate

class ReviewService:
    @staticmethod
    async def create_or_update_review(
        db: AsyncSession, 
        submission_id: int, 
        judge: User, 
        data: ReviewCreateUpdate
    ):
        submission = await db.get(Submission, submission_id)
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")

        team = await db.get(Team, submission.team_id)

        # Dynamic Track & Panel Assignment on Frontend Review Submission
        panel_id = data.panel_id if data.panel_id is not None else (team.panel_id if team else None)
        track_id = data.track_id if data.track_id is not None else (team.track_id if team else None)

        if team:
            if data.panel_id is not None:
                team.panel_id = data.panel_id
            if data.track_id is not None:
                team.track_id = data.track_id

        # Atomic PostgreSQL Upsert for Review
        stmt = insert(Review).values(
            submission_id=submission_id,
            judge_id=judge.user_id,
            panel_id=panel_id,
            track_id=track_id,
            score=data.score,
            comments=data.comments
        )
        stmt = stmt.on_conflict_do_update(
            constraint="unique_submission_judge",
            set_={
                "score": stmt.excluded.score,
                "comments": stmt.excluded.comments,
                "panel_id": stmt.excluded.panel_id,
                "track_id": stmt.excluded.track_id
            }
        )
        await db.execute(stmt)

        # Update Team Status if Admin
        if data.set_team_status and judge.role == UserRole.ADMIN:
            if team:
                team.status = data.set_team_status

        await db.commit()
        return {
            "status": "success",
            "assigned_panel_id": team.panel_id if team else None,
            "assigned_track_id": team.track_id if team else None
        }
