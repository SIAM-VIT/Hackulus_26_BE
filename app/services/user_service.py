from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.participant_profile import ParticipantProfile
from app.models.team import Team, TeamStatus
from app.models.event_config import EventConfig


class UserService:
    @staticmethod
    async def get_user_dashboard(db: AsyncSession, current_user: User):
        team_data = None
        members = []

        pp = current_user.participant_profile
        team_id = pp.team_id if pp else None

        if team_id:
            stmt = (
                select(Team)
                .options(
                    selectinload(Team.track),
                    selectinload(Team.problem_statement),
                    selectinload(Team.members).selectinload(ParticipantProfile.user)
                )
                .where(Team.team_id == team_id)
            )
            res = await db.execute(stmt)
            team = res.scalar_one_or_none()

            if team:
                team_data = {
                    "team_id": team.team_id,
                    "team_name": team.team_name,
                    "track_id": team.track_id,
                    "track_name": team.track.name if team.track else None,
                    "problem_statement_id": team.problem_statement_id,
                    "problem_statement": {
                        "id": team.problem_statement.id,
                        "title": team.problem_statement.title,
                        "description": team.problem_statement.description
                    } if team.problem_statement else None,
                    "status": team.status.value if hasattr(team.status, "value") else str(team.status),
                    "is_eliminated": team.status == TeamStatus.REJECTED
                }
                members = team.members

        config_res = await db.execute(select(EventConfig).where(EventConfig.id == 1))
        config = config_res.scalar_one_or_none()
        current_phase = config.current_phase if config else "Participants reach"
        windows = config.active_windows if config else {"review0": False, "review1": False, "review2": False}

        return {
            "user": {
                "user_id": current_user.user_id,
                "name": current_user.name,
                "email": current_user.email,
                "role": current_user.role,
                "is_leader": pp.is_leader if pp else False
            },
            "team": team_data,
            "members": [
                {
                    "user_id": m.user.user_id,
                    "name": m.user.name,
                    "email": m.user.email,
                    "is_leader": m.is_leader
                }
                for m in members
            ],
            "windows": windows,
            "currentPhase": current_phase
        }
