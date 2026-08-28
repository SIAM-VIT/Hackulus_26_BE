from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.panel import Panel
from app.models.team import Team
from app.utils.scheduler import assign_panels_to_teams

class PanelService:
    @staticmethod
    async def auto_assign_panels(db: AsyncSession):
        panels_res = await db.execute(select(Panel).order_by(Panel.panel_id))
        panels = [
            {"panel_id": p.panel_id, "track_id": p.track_id}
            for p in panels_res.scalars().all()
        ]

        if not panels:
            raise HTTPException(status_code=400, detail="No panels defined")

        teams_res = await db.execute(select(Team).order_by(Team.created_at))
        teams = [
            {"team_id": t.team_id, "track_id": t.track_id}
            for t in teams_res.scalars().all()
        ]

        assignments = assign_panels_to_teams(panels, teams)

        for assign in assignments:
            team = await db.get(Team, assign["team_id"])
            if team:
                team.panel_id = assign["panel_id"]

        await db.commit()
        return {"assigned": len(assignments), "assignments": assignments}
