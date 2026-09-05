from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert
from app.models.submission import Submission
from app.models.team import Team, TeamStatus
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
        if not team:
            raise HTTPException(status_code=404, detail="Team not found for this submission")

        # Determine review round from submission type if not provided
        review_round = data.review_round or (
            submission.type.value if hasattr(submission.type, "value") else str(submission.type)
        )

        track_id = data.track_id if data.track_id is not None else (team.track_id if team else None)
        panel_id = data.panel_id if data.panel_id is not None else judge.panel_id

        if team and data.track_id is not None:
            team.track_id = data.track_id

        # Calculate Total Score from 6 categories or fallback to provided score
        category_sum = (
            float(data.innovation_score or 0) +
            float(data.technical_complexity_score or 0) +
            float(data.feasibility_score or 0) +
            float(data.ui_ux_score or 0) +
            float(data.presentation_score or 0) +
            float(data.progress_score or 0)
        )
        total_score = data.score if (data.score is not None and category_sum == 0) else category_sum

        # Atomic PostgreSQL Upsert for Review
        stmt = insert(Review).values(
            submission_id=submission_id,
            team_id=team.team_id,
            judge_id=judge.user_id,
            panel_id=panel_id,
            track_id=track_id,
            review_round=review_round,
            innovation_score=data.innovation_score,
            technical_complexity_score=data.technical_complexity_score,
            feasibility_score=data.feasibility_score,
            ui_ux_score=data.ui_ux_score,
            presentation_score=data.presentation_score,
            progress_score=data.progress_score,
            score=total_score,
            comments=data.comments
        )
        stmt = stmt.on_conflict_do_update(
            constraint="unique_submission_judge",
            set_={
                "team_id": stmt.excluded.team_id,
                "panel_id": stmt.excluded.panel_id,
                "track_id": stmt.excluded.track_id,
                "review_round": stmt.excluded.review_round,
                "innovation_score": stmt.excluded.innovation_score,
                "technical_complexity_score": stmt.excluded.technical_complexity_score,
                "feasibility_score": stmt.excluded.feasibility_score,
                "ui_ux_score": stmt.excluded.ui_ux_score,
                "presentation_score": stmt.excluded.presentation_score,
                "progress_score": stmt.excluded.progress_score,
                "score": stmt.excluded.score,
                "comments": stmt.excluded.comments
            }
        )
        await db.execute(stmt)

        # Update Team Status if Admin
        if data.set_team_status and judge.role == UserRole.ADMIN:
            status_val = data.set_team_status.lower()
            if status_val in [s.value for s in TeamStatus]:
                team.status = TeamStatus(status_val)

        await db.commit()
        return {
            "status": "success",
            "message": "Review evaluated successfully",
            "submission_id": submission_id,
            "team_id": team.team_id,
            "total_score": total_score,
            "assigned_track_id": team.track_id if team else None
        }

    @staticmethod
    async def get_team_reviews(db: AsyncSession, team_id: int) -> Dict[str, Any]:
        team = await db.get(Team, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        stmt = (
            select(Review)
            .options(selectinload(Review.judge), selectinload(Review.panel), selectinload(Review.submission))
            .where(Review.team_id == team_id)
            .order_by(Review.created_at.desc())
        )
        res = await db.execute(stmt)
        reviews = res.scalars().all()

        reviews_list = []
        for r in reviews:
            reviews_list.append({
                "review_id": r.review_id,
                "submission_id": r.submission_id,
                "review_round": r.review_round,
                "judge_name": r.judge.name if r.judge else "Unknown",
                "panel_name": r.panel.name if r.panel else None,
                "innovation_score": float(r.innovation_score or 0),
                "technical_complexity_score": float(r.technical_complexity_score or 0),
                "feasibility_score": float(r.feasibility_score or 0),
                "ui_ux_score": float(r.ui_ux_score or 0),
                "presentation_score": float(r.presentation_score or 0),
                "progress_score": float(r.progress_score or 0),
                "total_score": float(r.score or 0),
                "comments": r.comments or "",
                "created_at": r.created_at
            })

        return {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "status": team.status.value if hasattr(team.status, "value") else str(team.status),
            "reviews": reviews_list
        }

    @staticmethod
    async def get_leaderboard(db: AsyncSession, round_name: Optional[str] = None) -> List[Dict[str, Any]]:
        stmt = (
            select(Team)
            .options(
                selectinload(Team.track),
                selectinload(Team.submissions).selectinload(Submission.reviews)
            )
        )
        res = await db.execute(stmt)
        teams = res.scalars().all()

        leaderboard = []
        for team in teams:
            team_reviews = []
            for s in team.submissions:
                for r in s.reviews:
                    if round_name is None or r.review_round == round_name:
                        team_reviews.append(r)

            if team_reviews:
                avg_score = sum(float(r.score or 0) for r in team_reviews) / len(team_reviews)
                avg_innovation = sum(float(r.innovation_score or 0) for r in team_reviews) / len(team_reviews)
                avg_tech = sum(float(r.technical_complexity_score or 0) for r in team_reviews) / len(team_reviews)
                avg_feasibility = sum(float(r.feasibility_score or 0) for r in team_reviews) / len(team_reviews)
                avg_ui_ux = sum(float(r.ui_ux_score or 0) for r in team_reviews) / len(team_reviews)
                avg_presentation = sum(float(r.presentation_score or 0) for r in team_reviews) / len(team_reviews)
                avg_progress = sum(float(r.progress_score or 0) for r in team_reviews) / len(team_reviews)
            else:
                avg_score = 0.0
                avg_innovation = avg_tech = avg_feasibility = avg_ui_ux = avg_presentation = avg_progress = 0.0

            leaderboard.append({
                "team_id": team.team_id,
                "team_name": team.team_name,
                "status": team.status.value if hasattr(team.status, "value") else str(team.status),
                "track_name": team.track.name if team.track else "No Track Selected",
                "reviews_count": len(team_reviews),
                "total_score": round(avg_score, 2),
                "scores_breakdown": {
                    "innovation": round(avg_innovation, 2),
                    "technical_complexity": round(avg_tech, 2),
                    "feasibility": round(avg_feasibility, 2),
                    "ui_ux": round(avg_ui_ux, 2),
                    "presentation": round(avg_presentation, 2),
                    "progress": round(avg_progress, 2)
                }
            })

        # Sort descending by total_score
        leaderboard.sort(key=lambda x: x["total_score"], reverse=True)
        return leaderboard
