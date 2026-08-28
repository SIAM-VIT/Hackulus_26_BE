from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.user import User
from app.models.team import Team, TeamStatus
from app.models.event_config import EventConfig
from app.schemas.team import AdminCreateTeamRequest, TeamMemberCreate
from app.services.team_service import TeamService
from app.services.panel_service import PanelService
from app.dependencies import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

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

@router.post("/assign-panels", summary="Admin: Run automatic panel assignment")
async def run_auto_panel_assignment(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return await PanelService.auto_assign_panels(db)

@router.post("/team/{team_id}/status", summary="Admin: Set team status")
async def set_team_status(
    team_id: int,
    status_val: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if status_val not in [s.value for s in TeamStatus]:
        raise HTTPException(status_code=400, detail="Invalid team status")

    team.status = TeamStatus(status_val)
    await db.commit()
    return {"ok": True, "status": team.status}

@router.post("/timeline/phase", summary="Admin: Set hackathon phase")
async def set_hackathon_phase(
    phase: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
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
