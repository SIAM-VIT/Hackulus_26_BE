from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.team import Team, TeamStatus
from app.models.event_config import EventConfig

class UserService:
    @staticmethod
    async def get_user_dashboard(db: AsyncSession, current_user: User):
        team_data = None
        members = []

        # Verify team elimination status and fetch team with track
        if current_user.team_id:
            stmt = select(Team).options(selectinload(Team.track)).where(Team.team_id == current_user.team_id)
            res = await db.execute(stmt)
            team = res.scalar_one_or_none()

            if team and team.status == TeamStatus.REJECTED:
                raise HTTPException(
                    status_code=403, 
                    detail="Your team has been eliminated and cannot perform this action."
                )
            
            if team:
                team_data = {
                    "team_id": team.team_id,
                    "team_name": team.team_name,
                    "track_id": team.track_id,
                    "track_name": team.track.name if team.track else None,
                    "problem_statement": team.problem_statement,
                    "idea": team.idea,
                    "status": team.status
                }

                members_res = await db.execute(
                    select(User).where(User.team_id == current_user.team_id)
                )
                members = members_res.scalars().all()

        # Fetch Event Config
        config_res = await db.execute(select(EventConfig).where(EventConfig.id == 1))
        config = config_res.scalar_one_or_none()
        
        current_phase = config.current_phase if config else "Participants reach"
        windows = config.active_windows if config else {"review1": False, "review2": False, "final": False}

        return {
            "user": {
                "user_id": current_user.user_id,
                "name": current_user.name,
                "email": current_user.email,
                "role": current_user.role,
                "is_leader": current_user.is_leader
            },
            "team": team_data,
            "members": [
                {
                    "user_id": m.user_id,
                    "name": m.name,
                    "email": m.email,
                    "is_leader": m.is_leader
                }
                for m in members
            ],
            "windows": windows,
            "currentPhase": current_phase
        }
