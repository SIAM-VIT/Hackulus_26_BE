from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.user import User
from app.models.team import Team, TeamStatus
from app.models.submission import Submission
from app.models.review import Review
from app.models.event_config import EventConfig
from app.schemas.team import AdminCreateTeamRequest, TeamMemberCreate
from app.schemas.review import ReviewCreateUpdate
from app.services.team_service import TeamService
from app.services.review_service import ReviewService
from app.dependencies import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

class TimelinePhaseRequest(BaseModel):
    phase: str

class TeamStatusRequest(BaseModel):
    status: str

@router.post(
    "/team/create-with-members", 
    status_code=status.HTTP_201_CREATED,
    summary="Admin: Create a team with members"
)
async def create_team_with_members(
    data: AdminCreateTeamRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return await TeamService.create_team_with_members_by_admin(db, data)

@router.post(
    "/team/{team_id}/add-member", 
    status_code=status.HTTP_201_CREATED,
    summary="Admin: Add a single member to an existing team"
)
async def add_member_to_team(
    team_id: int,
    data: TeamMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return await TeamService.add_single_member_to_team(db, team_id, data)

@router.get("/teams", summary="Admin: List all teams for Admin Dashboard")
async def list_admin_teams(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    stmt = select(Team).options(selectinload(Team.members), selectinload(Team.track))
    res = await db.execute(stmt)
    teams = res.scalars().all()

    result = []
    for team in teams:
        result.append({
            "team_id": team.team_id,
            "team_name": team.team_name,
            "track_name": team.track.name if team.track else "No Track Selected",
            "status": team.status.value if hasattr(team.status, "value") else str(team.status),
            "problem_statement": team.problem_statement or "",
            "idea": team.idea or "",
            "members": [
                {
                    "member_id": m.user_id,
                    "user_id": m.user_id,
                    "name": m.name,
                    "email": m.email,
                    "registration_number": m.registration_number,
                    "hostel_block": m.hostel_block,
                    "is_leader": m.is_leader
                }
                for m in team.members
            ]
        })

    return {"teams": result}

@router.get("/team/{team_id}", summary="Admin: Get detailed team info and submissions")
async def get_admin_team_details(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    stmt = select(Team).options(selectinload(Team.members), selectinload(Team.track), selectinload(Team.submissions)).where(Team.team_id == team_id)
    res = await db.execute(stmt)
    team = res.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return {
        "team": {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "track_name": team.track.name if team.track else "No Track Selected",
            "status": team.status.value if hasattr(team.status, "value") else str(team.status),
            "problem_statement": team.problem_statement or "",
            "idea": team.idea or ""
        },
        "members": [
            {
                "member_id": m.user_id,
                "user_id": m.user_id,
                "name": m.name,
                "email": m.email,
                "registration_number": m.registration_number,
                "hostel_block": m.hostel_block,
                "is_leader": m.is_leader
            }
            for m in team.members
        ],
        "submissions": [
            {
                "submission_id": s.submission_id,
                "type": s.type.value if hasattr(s.type, "value") else str(s.type),
                "title": s.title or "",
                "description": s.description or "",
                "links": s.links or {},
                "status": s.status
            }
            for s in team.submissions
        ]
    }

@router.get("/submission/{submission_id}", summary="Admin: Get reviews for a submission")
async def get_admin_submission_reviews(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    res = await db.execute(select(Review).where(Review.submission_id == submission_id))
    reviews = res.scalars().all()
    return {
        "reviews": [
            {
                "review_id": r.review_id,
                "submission_id": r.submission_id,
                "judge_id": r.judge_id,
                "score": r.score,
                "comments": r.comments
            }
            for r in reviews
        ]
    }

@router.post("/submission/{submission_id}/review", summary="Admin/Judge: Submit score for a submission")
async def create_admin_submission_review(
    submission_id: int,
    data: ReviewCreateUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return await ReviewService.create_or_update_review(db, submission_id, current_admin, data)

@router.post("/team/{team_id}/status", summary="Admin: Set team status (e.g. rejected/shortlisted)")
async def set_team_status(
    team_id: int,
    data: TeamStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    status_val = data.status.lower()
    if status_val not in [s.value for s in TeamStatus]:
        raise HTTPException(status_code=400, detail="Invalid team status")

    team.status = TeamStatus(status_val)
    await db.commit()
    return {"ok": True, "status": team.status}

@router.get("/timeline/phase", summary="Admin: Get current hackathon phase")
async def get_hackathon_phase(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    res = await db.execute(select(EventConfig).where(EventConfig.id == 1))
    config = res.scalar_one_or_none()
    current_phase = config.current_phase if config else "Participants reach"
    return {"currentPhase": current_phase}

@router.post("/timeline/phase", summary="Admin: Set hackathon phase")
async def set_hackathon_phase(
    data: TimelinePhaseRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    phase = data.phase
    res = await db.execute(select(EventConfig).where(EventConfig.id == 1))
    config = res.scalar_one_or_none()
    if not config:
        config = EventConfig(id=1)
        db.add(config)

    config.current_phase = phase

    # Auto update submission active windows
    if phase == "Review 1":
        config.active_windows = {"review1": True, "review2": False, "final": False}
    elif phase == "Review 2":
        config.active_windows = {"review1": False, "review2": True, "final": False}
    elif phase == "Final Review":
        config.active_windows = {"review1": False, "review2": False, "final": True}
    else:
        config.active_windows = {"review1": False, "review2": False, "final": False}

    await db.commit()
    return {"ok": True, "current_phase": config.current_phase, "windows": config.active_windows}
