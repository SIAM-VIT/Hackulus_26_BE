from typing import List
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.user import User
from app.models.track import Track
from app.models.problem_statement import ProblemStatement
from app.schemas.team import TeamAssignTrack
from app.services.team_service import TeamService
from app.dependencies import get_current_user, get_current_judge_or_admin

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.get("/my-team", summary="Get current logged in user's team details (name, members, leader)")
async def get_my_team(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await TeamService.get_my_team_details(db, current_user)

@router.get("/tracks", summary="List all tracks")
async def list_tracks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(select(Track).order_by(Track.track_id))
    tracks = res.scalars().all()
    return [{"track_id": t.track_id, "name": t.name, "description": t.description} for t in tracks]

@router.get("/tracks/{track_id}/problem-statements", summary="List problem statements for a specific track when clicked")
async def get_track_problem_statements(
    track_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(
        select(ProblemStatement)
        .where(ProblemStatement.track_id == track_id)
        .order_by(ProblemStatement.id)
    )
    ps_list = res.scalars().all()
    return [
        {
            "id": ps.id,
            "title": ps.title,
            "description": ps.description,
            "track_id": ps.track_id
        }
        for ps in ps_list
    ]

@router.put("/problem-statement", summary="Update team's problem statement")
async def update_problem_statement(
    problem_statement: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await TeamService.update_problem_statement(db, current_user, problem_statement)

@router.put("/{team_id}/assign-track", summary="Judges/Admin: Dynamically assign track to team")
async def assign_track(
    team_id: int,
    data: TeamAssignTrack,
    db: AsyncSession = Depends(get_db),
    current_judge: User = Depends(get_current_judge_or_admin)
):
    return await TeamService.update_team_track(db, team_id, data)
