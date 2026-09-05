from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from app.models.team import Team, TeamStatus
from app.models.user import User, UserRole
from app.models.participant_profile import ParticipantProfile
from app.models.track import Track
from app.models.problem_statement import ProblemStatement
from app.schemas.team import AdminCreateTeamRequest, TeamMemberCreate, TeamAssignTrack, TeamBatchStatusUpdate


class TeamService:
    @staticmethod
    async def create_team_with_members_by_admin(db: AsyncSession, data: AdminCreateTeamRequest):
        existing_team = await db.execute(select(Team).where(Team.team_name == data.team_name))
        if existing_team.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"Team '{data.team_name}' already exists")

        member_emails = [m.email for m in data.members]
        existing_users = await db.execute(select(User.email).where(User.email.in_(member_emails)))
        found_emails = existing_users.scalars().all()
        if found_emails:
            raise HTTPException(status_code=400, detail=f"Emails already registered: {', '.join(found_emails)}")

        if data.problem_statement_id is not None:
            ps = await db.get(ProblemStatement, data.problem_statement_id)
            if not ps:
                raise HTTPException(status_code=404, detail="Problem statement not found")

        new_team = Team(
            team_name=data.team_name,
            track_id=data.track_id,
            problem_statement_id=data.problem_statement_id,
            status=TeamStatus.PENDING
        )
        db.add(new_team)
        await db.flush()

        created_users = []
        for member in data.members:
            pwd = member.password or member.registration_number or "password123"
            user = User(
                name=member.name,
                email=member.email,
                password_hash=pwd,
                role=UserRole.PARTICIPANT,
            )
            db.add(user)
            await db.flush()

            profile = ParticipantProfile(
                user_id=user.user_id,
                team_id=new_team.team_id,
                is_leader=member.is_leader,
                registration_number=member.registration_number,
                hostel_block=member.hostel_block,
                extra_info=member.extra_info or {}
            )
            db.add(profile)
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
                "problem_statement_id": new_team.problem_statement_id,
                "members_count": len(created_users)
            }
        }

    @staticmethod
    async def add_single_member_to_team(db: AsyncSession, team_id: int, member_data: TeamMemberCreate):
        team = await db.get(Team, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        existing_user = await db.execute(select(User).where(User.email == member_data.email))
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User email already exists")

        pwd = member_data.password or member_data.registration_number or "password123"
        new_user = User(
            name=member_data.name,
            email=member_data.email,
            password_hash=pwd,
            role=UserRole.PARTICIPANT,
        )
        db.add(new_user)
        await db.flush()

        profile = ParticipantProfile(
            user_id=new_user.user_id,
            team_id=team_id,
            is_leader=member_data.is_leader,
            registration_number=member_data.registration_number,
            hostel_block=member_data.hostel_block,
            extra_info=member_data.extra_info or {}
        )
        db.add(profile)
        await db.commit()
        await db.refresh(new_user)
        return {"message": "Member added successfully", "user_id": new_user.user_id}

    @staticmethod
    async def update_problem_statement(db: AsyncSession, user: User, problem_statement_id: int):
        pp = user.participant_profile
        if not pp:
            raise HTTPException(status_code=400, detail="User must belong to a team")
        if not pp.is_leader:
            raise HTTPException(status_code=403, detail="Only team leader can change problem statement")

        ps = await db.get(ProblemStatement, problem_statement_id)
        if not ps:
            raise HTTPException(status_code=404, detail="Problem statement not found")

        team = await db.get(Team, pp.team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        team.problem_statement_id = problem_statement_id
        await db.commit()
        return {"success": True, "message": "Problem statement updated", "problem_statement_id": problem_statement_id}

    @staticmethod
    async def update_team_track(db: AsyncSession, team_id: int, data: TeamAssignTrack):
        team = await db.get(Team, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        if data.track_id is not None:
            team.track_id = data.track_id
        await db.commit()
        await db.refresh(team)
        return {"success": True, "message": "Team track updated successfully", "team_id": team.team_id, "track_id": team.track_id}

    @staticmethod
    async def batch_update_status(db: AsyncSession, data: TeamBatchStatusUpdate):
        status_val = data.status.lower()
        if status_val not in [s.value for s in TeamStatus]:
            raise HTTPException(status_code=400, detail=f"Invalid team status '{data.status}'")
        res = await db.execute(select(Team).where(Team.team_id.in_(data.team_ids)))
        teams = res.scalars().all()
        for team in teams:
            team.status = TeamStatus(status_val)
        await db.commit()
        return {"success": True, "message": f"Updated status to '{status_val}' for {len(teams)} teams", "updated_teams_count": len(teams)}

    update_team_track_and_panel = update_team_track

    @staticmethod
    async def get_my_team_details(db: AsyncSession, user: User):
        pp = user.participant_profile
        if not pp:
            raise HTTPException(status_code=400, detail="User is not assigned to any team")

        stmt = (
            select(Team)
            .options(
                selectinload(Team.members).selectinload(ParticipantProfile.user),
                selectinload(Team.track),
                selectinload(Team.problem_statement)
            )
            .where(Team.team_id == pp.team_id)
        )
        res = await db.execute(stmt)
        team = res.scalar_one_or_none()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        return {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "status": team.status.value if hasattr(team.status, "value") else str(team.status),
            "problem_statement_id": team.problem_statement_id,
            "problem_statement": {
                "id": team.problem_statement.id,
                "title": team.problem_statement.title,
                "description": team.problem_statement.description
            } if team.problem_statement else None,
            "track": {"track_id": team.track.track_id, "name": team.track.name, "description": team.track.description} if team.track else None,
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
            ]
        }
