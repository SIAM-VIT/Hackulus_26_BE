from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User, UserRole
from app.models.team import Team, TeamStatus
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from app.core.security import create_access_token

class AuthService:
    @staticmethod
    async def signup_user(db: AsyncSession, data: SignupRequest) -> TokenResponse:
        # Check existing user
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Check or create team
        team_result = await db.execute(select(Team).where(Team.team_name == data.team_name))
        team = team_result.scalar_one_or_none()

        if not team:
            team = Team(
                team_name=data.team_name,
                track_id=data.track_id,
                status=TeamStatus.PENDING
            )
            db.add(team)
            await db.flush()

        # Create user (plain text password per non-prod requirement)
        new_user = User(
            name=data.name,
            email=data.email,
            password_hash=data.password,
            role=UserRole.PARTICIPANT,
            team_id=team.team_id,
            is_leader=data.is_leader,
            extra_info=data.extra_info
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        token = create_access_token({
            "sub": str(new_user.user_id),
            "email": new_user.email,
            "role": new_user.role,
            "team_id": new_user.team_id,
            "is_leader": new_user.is_leader
        })

        return TokenResponse(access_token=token)

    @staticmethod
    async def login_user(db: AsyncSession, data: LoginRequest) -> TokenResponse:
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        # Plain text password verification as requested
        if user.password_hash != data.password:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        token = create_access_token({
            "sub": str(user.user_id),
            "email": user.email,
            "role": user.role,
            "team_id": user.team_id,
            "panel_id": user.panel_id,
            "is_leader": user.is_leader
        })

        return TokenResponse(access_token=token)
