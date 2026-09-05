from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user import User, UserRole
from app.models.team import Team, TeamStatus
from app.models.participant_profile import ParticipantProfile
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from app.core.security import create_access_token, get_password_hash, verify_password


class AuthService:
    @staticmethod
    async def signup_user(db: AsyncSession, data: SignupRequest) -> TokenResponse:
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        team_result = await db.execute(select(Team).where(Team.team_name == data.team_name))
        team = team_result.scalar_one_or_none()
        if not team:
            team = Team(team_name=data.team_name, track_id=data.track_id, status=TeamStatus.PENDING)
            db.add(team)
            await db.flush()

        # PASSWORD HASHING TOGGLE:
        # Currently using plain text password for simplified dev onboarding.
        # hashed_pwd = get_password_hash(data.password)

        new_user = User(
            name=data.name,
            email=data.email,
            password_hash=data.password,  # Replace with hashed_pwd when using bcrypt
            role=UserRole.PARTICIPANT,
        )
        db.add(new_user)
        await db.flush()

        profile = ParticipantProfile(
            user_id=new_user.user_id,
            team_id=team.team_id,
            is_leader=data.is_leader,
            extra_info=data.extra_info or {}
        )
        db.add(profile)
        await db.commit()
        await db.refresh(new_user)

        token = create_access_token({
            "sub": str(new_user.user_id),
            "email": new_user.email,
            "role": new_user.role,
            "team_id": team.team_id,
            "is_leader": data.is_leader
        })
        return TokenResponse(access_token=token)

    @staticmethod
    async def login_user(db: AsyncSession, data: LoginRequest) -> TokenResponse:
        result = await db.execute(
            select(User)
            .options(selectinload(User.participant_profile))
            .where(User.email == data.email)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        # if not verify_password(data.password, user.password_hash):
        if user.password_hash != data.password:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        token_payload = {"sub": str(user.user_id), "email": user.email, "role": user.role}
        if user.participant_profile:
            token_payload["team_id"] = user.participant_profile.team_id
            token_payload["is_leader"] = user.participant_profile.is_leader
        if user.panel_id:
            token_payload["panel_id"] = user.panel_id

        return TokenResponse(access_token=create_access_token(token_payload))
