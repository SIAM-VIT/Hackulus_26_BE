from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.services.panel_service import PanelService
from app.dependencies import get_current_user, get_current_judge_or_admin

router = APIRouter(prefix="/panels", tags=["Panels"])

@router.get("", summary="List all panels")
async def list_panels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns all 5 panels with their assigned team counts.
    """
    return await PanelService.list_panels(db)

@router.get("/{panel_id}/teams", summary="List teams assigned to a panel")
async def get_panel_teams(
    panel_id: int,
    db: AsyncSession = Depends(get_db),
    current_judge: User = Depends(get_current_judge_or_admin)
):
    """
    Returns all teams assigned to the selected panel along with their track,
    problem statement, and submission status.
    """
    return await PanelService.get_panel_teams(db, panel_id)

@router.get("/{panel_id}/team/{team_id}", summary="Get full team details and submissions for panel evaluation")
async def get_panel_team_evaluation_details(
    panel_id: int,
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_judge: User = Depends(get_current_judge_or_admin)
):
    """
    Provides the complete evaluation view of a team to the panel evaluators:
    - Team info, members, leader
    - Chosen track and problem statement
    - Submissions made (Review 0, Review 1, Review 2 with GitHub, PPT, demo links)
    - Previous evaluation scores and comments
    """
    return await PanelService.get_panel_team_details(db, panel_id, team_id)
