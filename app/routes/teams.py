from typing import List
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.user import User
from app.models.panel import Panel
from app.models.track import Track
from app.schemas.team import TeamAssignTrackPanel, TeamResponse
from app.schemas.panel import PanelResponse
from app.services.team_service import TeamService
from app.dependencies import get_current_user, get_current_judge_or_admin

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.get("/panels", response_model=List[PanelResponse], summary="List all panels for dropdown")
async def list_panels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(select(Panel).order_by(Panel.panel_id))
    return res.scalars().all()

@router.get("/tracks", summary="List all tracks for dropdown")
async def list_tracks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(select(Track).order_by(Track.track_id))
    return res.scalars().all()

@router.put("/problem-statement")
async def update_problem_statement(
    problem_statement: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await TeamService.update_problem_statement(db, current_user, problem_statement)

@router.put("/{team_id}/assign-track-panel", summary="Judges/Admin: Dynamically assign track & panel to team from dropdown")
async def assign_track_and_panel(
    team_id: int,
    data: TeamAssignTrackPanel,
    db: AsyncSession = Depends(get_db),
    current_judge: User = Depends(get_current_judge_or_admin)
):
    return await TeamService.update_team_track_and_panel(db, team_id, data)
