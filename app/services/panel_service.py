from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.panel import Panel
from app.models.team import Team
from app.models.participant_profile import ParticipantProfile
from app.models.submission import Submission
from app.models.review import Review


class PanelService:
    @staticmethod
    async def list_panels(db: AsyncSession) -> List[Dict[str, Any]]:
        stmt = select(Panel).options(selectinload(Panel.judges)).order_by(Panel.panel_id)
        res = await db.execute(stmt)
        panels = res.scalars().all()
        return [
            {
                "panel_id": p.panel_id,
                "name": p.name,
                "description": p.description,
                "judges_count": len(p.judges),
                "created_at": p.created_at
            }
            for p in panels
        ]

    @staticmethod
    async def get_panel_teams(db: AsyncSession, panel_id: int) -> Dict[str, Any]:
        panel = await db.get(Panel, panel_id)
        if not panel:
            raise HTTPException(status_code=404, detail="Panel not found")

        # Any panel can evaluate any team in the hackathon
        stmt = (
            select(Team)
            .options(
                selectinload(Team.members).selectinload(ParticipantProfile.user),
                selectinload(Team.track),
                selectinload(Team.problem_statement),
                selectinload(Team.submissions).selectinload(Submission.reviews)
            )
            .order_by(Team.team_id)
        )
        res = await db.execute(stmt)
        teams = res.scalars().all()

        team_list = []
        for team in teams:
            latest = team.submissions[-1] if team.submissions else None
            # Check if this panel has reviewed any of the team's submissions
            panel_reviewed = any(
                r.panel_id == panel_id
                for s in team.submissions
                for r in s.reviews
            )
            team_list.append({
                "team_id": team.team_id,
                "team_name": team.team_name,
                "track_name": team.track.name if team.track else "No Track Selected",
                "track_id": team.track_id,
                "problem_statement_id": team.problem_statement_id,
                "problem_statement_title": team.problem_statement.title if team.problem_statement else None,
                "status": team.status.value if hasattr(team.status, "value") else str(team.status),
                "members_count": len(team.members),
                "submissions_count": len(team.submissions),
                "evaluated_by_this_panel": panel_reviewed,
                "latest_submission_type": (
                    latest.type.value if (latest and hasattr(latest.type, "value"))
                    else (latest.type if latest else None)
                )
            })

        return {
            "panel": {"panel_id": panel.panel_id, "name": panel.name, "description": panel.description},
            "teams": team_list
        }

    @staticmethod
    async def get_panel_team_details(db: AsyncSession, panel_id: int, team_id: int) -> Dict[str, Any]:
        panel = await db.get(Panel, panel_id)
        if not panel:
            raise HTTPException(status_code=404, detail="Panel not found")

        stmt = (
            select(Team)
            .options(
                selectinload(Team.members).selectinload(ParticipantProfile.user),
                selectinload(Team.track),
                selectinload(Team.problem_statement),
                selectinload(Team.submissions).selectinload(Submission.reviews).selectinload(Review.judge)
            )
            .where(Team.team_id == team_id)
        )
        res = await db.execute(stmt)
        team = res.scalar_one_or_none()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        submissions_data = []
        for s in team.submissions:
            submissions_data.append({
                "submission_id": s.submission_id,
                "type": s.type.value if hasattr(s.type, "value") else str(s.type),
                "title": s.title,
                "description": s.description,
                "links": s.links or {},
                "status": s.status.value if hasattr(s.status, "value") else str(s.status),
                "created_at": s.created_at,
                "reviews": [
                    {
                        "review_id": r.review_id,
                        "judge_id": r.judge_id,
                        "judge_name": r.judge.name if r.judge else "Unknown Judge",
                        "review_round": r.review_round,
                        "innovation_score": float(r.innovation_score or 0),
                        "technical_complexity_score": float(r.technical_complexity_score or 0),
                        "feasibility_score": float(r.feasibility_score or 0),
                        "ui_ux_score": float(r.ui_ux_score or 0),
                        "presentation_score": float(r.presentation_score or 0),
                        "progress_score": float(r.progress_score or 0),
                        "total_score": float(r.score or 0),
                        "comments": r.comments or "",
                        "created_at": r.created_at
                    }
                    for r in s.reviews
                ]
            })

        return {
            "panel": {"panel_id": panel.panel_id, "name": panel.name},
            "team": {
                "team_id": team.team_id,
                "team_name": team.team_name,
                "status": team.status.value if hasattr(team.status, "value") else str(team.status),
                "track_id": team.track_id,
                "track_name": team.track.name if team.track else "No Track Selected",
                "track_description": team.track.description if team.track else "",
                "problem_statement_id": team.problem_statement_id,
                "problem_statement": {
                    "id": team.problem_statement.id,
                    "title": team.problem_statement.title,
                    "description": team.problem_statement.description
                } if team.problem_statement else None
            },
            "members": [
                {
                    "user_id": m.user.user_id,
                    "name": m.user.name,
                    "email": m.user.email,
                    "registration_number": m.registration_number,
                    "hostel_block": m.hostel_block,
                    "is_leader": m.is_leader
                }
                for m in team.members
            ],
            "submissions": submissions_data
        }
