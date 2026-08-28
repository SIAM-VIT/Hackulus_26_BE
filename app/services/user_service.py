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
        # Verify team elimination status
        if current_user.team_id:
            team = await db.get(Team, current_user.team_id)
            if team and team.status == TeamStatus.REJECTED:
                raise HTTPException(
                    status_code=403, 
                    detail="Your team has been eliminated and cannot perform this action."
                )
        else:
            team = None

        # Fetch team members
        members = []
        if current_user.team_id:
            res = await db.execute(
                select(User).where(User.team_id == current_user.team_id)
            )
            members = res.scalars().all()

        # Fetch Event Config
        config_res = await db.execute(select(EventConfig).where(EventConfig.id == 1))
        config = config_res.scalar_one_or_none()
        
        current_phase = config.current_phase if config else "Participants reach"
        windows = config.active_windows if config else {"review1": False, "review2": False, "final": False}

        return {
            "user": current_user,
            "team": team,
            "members": members,
            "windows": windows,
            "currentPhase": current_phase
        }
