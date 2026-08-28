from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.team import Team, TeamStatus
from app.models.user import User, UserRole
from app.schemas.team import AdminCreateTeamRequest, TeamMemberCreate, TeamAssignTrackPanel

from app.core.security import get_password_hash

class TeamService:
    @staticmethod
    async def create_team_with_members_by_admin(
        db: AsyncSession, 
        data: AdminCreateTeamRequest
    ):
        # 1. Check existing team_name
        existing_team = await db.execute(
            select(Team).where(Team.team_name == data.team_name)
        )
        if existing_team.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"Team '{data.team_name}' already exists")

        # 2. Check if any member email is already registered
        member_emails = [m.email for m in data.members]
        existing_users = await db.execute(
            select(User.email).where(User.email.in_(member_emails))
        )
        found_emails = existing_users.scalars().all()
        if found_emails:
            raise HTTPException(
                status_code=400, 
                detail=f"Emails already registered: {', '.join(found_emails)}"
            )

        # 3. Create Team
        new_team = Team(
            team_name=data.team_name,
            track_id=data.track_id,
            panel_id=data.panel_id,
            problem_statement=data.problem_statement,
            idea=data.idea,
            status=TeamStatus.PENDING
        )
        db.add(new_team)
        await db.flush()

        # 4. Create Members
        created_users = []
        for member in data.members:
            # PASSWORD HASHING TOGGLE:
            # To hash passwords with bcrypt, use: password_hash=get_password_hash(member.password)
            user = User(
                name=member.name,
                email=member.email,
                password_hash=member.password,
                role=UserRole.PARTICIPANT,
                team_id=new_team.team_id,
                is_leader=member.is_leader,
                hostel_block=member.hostel_block,
                extra_info=member.extra_info
            )
            db.add(user)
            created_users.append(user)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Database constraint conflict: Team name or email already registered")

        await db.refresh(new_team)

        return {
            "message": "Team and members created successfully",
            "team": {
                "team_id": new_team.team_id,
                "team_name": new_team.team_name,
                "track_id": new_team.track_id,
                "panel_id": new_team.panel_id,
                "members_count": len(created_users)
            }
        }

    @staticmethod
    async def add_single_member_to_team(
        db: AsyncSession, 
        team_id: int, 
        member_data: TeamMemberCreate
    ):
        team = await db.get(Team, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        existing_user = await db.execute(select(User).where(User.email == member_data.email))
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User email already exists")

        # PASSWORD HASHING TOGGLE:
        # To hash passwords with bcrypt, use: password_hash=get_password_hash(member_data.password)
        new_user = User(
            name=member_data.name,
            email=member_data.email,
            password_hash=member_data.password,
            role=UserRole.PARTICIPANT,
            team_id=team_id,
            is_leader=member_data.is_leader,
            hostel_block=member_data.hostel_block,
            extra_info=member_data.extra_info
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return {"message": "Member added successfully", "user_id": new_user.user_id}

    @staticmethod
    async def update_problem_statement(db: AsyncSession, user: User, problem_statement: str):
        if not user.team_id:
            raise HTTPException(status_code=400, detail="User must belong to a team")
        if not user.is_leader:
            raise HTTPException(status_code=403, detail="Only team leader can change problem statement")

        team = await db.get(Team, user.team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        team.problem_statement = problem_statement
        await db.commit()
        return {"success": True, "message": "Problem statement updated"}

    @staticmethod
    async def update_team_track_and_panel(
        db: AsyncSession, 
        team_id: int, 
        data: TeamAssignTrackPanel
    ):
        team = await db.get(Team, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        if data.track_id is not None:
            team.track_id = data.track_id
        if data.panel_id is not None:
            team.panel_id = data.panel_id

        await db.commit()
        await db.refresh(team)

        return {
            "success": True,
            "message": "Team track and panel updated successfully",
            "team_id": team.team_id,
            "track_id": team.track_id,
            "panel_id": team.panel_id
        }
