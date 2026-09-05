from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, status, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.user import User
from app.models.participant_profile import ParticipantProfile
from app.models.team import Team, TeamStatus
from app.models.panel import Panel
from app.models.problem_statement import ProblemStatement
from app.models.submission import Submission
from app.models.review import Review
from app.models.event_config import EventConfig
from app.schemas.team import AdminCreateTeamRequest, TeamMemberCreate, TeamBatchStatusUpdate
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

@router.post(
    "/teams/batch-status",
    summary="Admin: Batch update teams status (Review 1 Elimination / Shortlisting)"
)
async def batch_update_team_status(
    data: TeamBatchStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Allows Admin to batch shortlist or eliminate (reject) teams after Review 1.
    """
    return await TeamService.batch_update_status(db, data)

@router.get("/teams", summary="Admin: List all teams with tracks")
async def list_admin_teams(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    stmt = select(Team).options(
        selectinload(Team.members).selectinload(ParticipantProfile.user),
        selectinload(Team.track),
        selectinload(Team.problem_statement)
    )
    res = await db.execute(stmt)
    teams = res.scalars().all()

    result = []
    for team in teams:
        result.append({
            "team_id": team.team_id,
            "team_name": team.team_name,
            "track_id": team.track_id,
            "track_name": team.track.name if team.track else "No Track Selected",
            "status": team.status.value if hasattr(team.status, "value") else str(team.status),
            "problem_statement_id": team.problem_statement_id,
            "problem_statement_title": team.problem_statement.title if team.problem_statement else None,
            "members": [
                {
                    "member_id": m.user.user_id,
                    "user_id": m.user.user_id,
                    "name": m.user.name,
                    "email": m.user.email,
                    "registration_number": m.registration_number,
                    "hostel_block": m.hostel_block,
                    "is_leader": m.is_leader
                }
                for m in team.members
            ]
        })

    return {"teams": result}

@router.get("/team/{team_id}", summary="Admin: Get detailed team info, submissions and reviews")
async def get_admin_team_details(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
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

    submissions_list = []
    for s in team.submissions:
        reviews_list = []
        for r in s.reviews:
            reviews_list.append({
                "review_id": r.review_id,
                "judge_id": r.judge_id,
                "judge_name": r.judge.name if r.judge else "Unknown",
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
            })

        submissions_list.append({
            "submission_id": s.submission_id,
            "type": s.type.value if hasattr(s.type, "value") else str(s.type),
            "title": s.title or "",
            "description": s.description or "",
            "links": s.links or {},
            "status": s.status.value if hasattr(s.status, "value") else str(s.status),
            "reviews": reviews_list
        })

    return {
        "team": {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "track_id": team.track_id,
            "track_name": team.track.name if team.track else "No Track Selected",
            "status": team.status.value if hasattr(team.status, "value") else str(team.status),
            "problem_statement_id": team.problem_statement_id,
            "problem_statement": {
                "id": team.problem_statement.id,
                "title": team.problem_statement.title,
                "description": team.problem_statement.description
            } if team.problem_statement else None
        },
        "members": [
            {
                "member_id": m.user.user_id,
                "user_id": m.user.user_id,
                "name": m.user.name,
                "email": m.user.email,
                "registration_number": m.registration_number,
                "hostel_block": m.hostel_block,
                "is_leader": m.is_leader
            }
            for m in team.members
        ],
        "submissions": submissions_list
    }

@router.get("/submission/{submission_id}", summary="Admin: Get reviews for a submission")
async def get_admin_submission_reviews(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    res = await db.execute(
        select(Review)
        .options(selectinload(Review.judge))
        .where(Review.submission_id == submission_id)
    )
    reviews = res.scalars().all()
    return {
        "reviews": [
            {
                "review_id": r.review_id,
                "submission_id": r.submission_id,
                "judge_id": r.judge_id,
                "judge_name": r.judge.name if r.judge else "Unknown",
                "review_round": r.review_round,
                "innovation_score": float(r.innovation_score or 0),
                "technical_complexity_score": float(r.technical_complexity_score or 0),
                "feasibility_score": float(r.feasibility_score or 0),
                "ui_ux_score": float(r.ui_ux_score or 0),
                "presentation_score": float(r.presentation_score or 0),
                "progress_score": float(r.progress_score or 0),
                "total_score": float(r.score or 0),
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

@router.get("/leaderboard", summary="Admin: View consolidated leaderboard and rubric scores")
async def get_admin_leaderboard(
    round_name: Optional[str] = Query(None, description="Filter by round: review1 or review2"),
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return await ReviewService.get_leaderboard(db, round_name)

@router.get("/timeline/phase", summary="Admin: Get current hackathon phase")
async def get_hackathon_phase(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    res = await db.execute(select(EventConfig).where(EventConfig.id == 1))
    config = res.scalar_one_or_none()
    current_phase = config.current_phase if config else "Participants reach"
    windows = config.active_windows if config else {"review0": False, "review1": False, "review2": False}
    return {"currentPhase": current_phase, "windows": windows}

@router.post("/timeline/phase", summary="Admin: Set hackathon phase and update active windows")
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
    phase_lower = phase.lower()

    # Auto update submission active windows
    if "review 0" in phase_lower or "review0" in phase_lower:
        config.active_windows = {"review0": True, "review1": False, "review2": False}
    elif "review 1" in phase_lower and "elimination" not in phase_lower:
        config.active_windows = {"review0": False, "review1": True, "review2": False}
    elif "review 2" in phase_lower or "final" in phase_lower:
        config.active_windows = {"review0": False, "review1": False, "review2": True}
    else:
        config.active_windows = {"review0": False, "review1": False, "review2": False}

    await db.commit()
    return {"ok": True, "current_phase": config.current_phase, "windows": config.active_windows}
