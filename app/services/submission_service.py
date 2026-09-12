from typing import Optional, Dict, Any
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.submission import Submission, SubmissionType, SubmissionStatus
from app.models.team import Team, TeamStatus
from app.models.track import Track
from app.models.problem_statement import ProblemStatement
from app.models.user import User
from app.models.event_config import EventConfig
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionUpdate,
    Review0SubmissionCreate,
    Review1SubmissionCreate,
    Review2SubmissionCreate
)


class SubmissionService:
    @staticmethod
    async def create_submission(db: AsyncSession, user: User, data: SubmissionCreate):
        pp = user.participant_profile
        if not pp:
            raise HTTPException(status_code=400, detail="User must belong to a team")
        if not pp.is_leader:
            raise HTTPException(status_code=403, detail="Only the team leader can submit")

        team = await db.get(Team, pp.team_id)
        if team and team.status == TeamStatus.REJECTED:
            raise HTTPException(status_code=403, detail="Your team has been eliminated.")

        sub_type = data.type.lower()
        config_res = await db.execute(select(EventConfig).where(EventConfig.id == 1))
        config = config_res.scalar_one_or_none()
        windows = config.active_windows if config else {}
        window_key = "review2" if sub_type == "final" else sub_type

        if not windows.get(window_key, False):
            raise HTTPException(status_code=403, detail=f"{data.type} submissions are currently closed")

        links_data = data.links or {}
        existing_res = await db.execute(
            select(Submission).where(
                Submission.team_id == pp.team_id,
                Submission.type == SubmissionType(sub_type)
            )
        )
        existing = existing_res.scalar_one_or_none()
        if existing:
            if data.title: existing.title = data.title
            if data.description: existing.description = data.description
            if data.links: existing.links = links_data
            existing.status = SubmissionStatus.SUBMITTED
            await db.commit()
            await db.refresh(existing)
            return existing

        submission = Submission(
            team_id=pp.team_id,
            submitted_by=user.user_id,
            type=SubmissionType(sub_type),
            title=data.title or f"{sub_type.capitalize()} Submission",
            description=data.description,
            links=links_data,
            status=SubmissionStatus.SUBMITTED
        )
        db.add(submission)
        await db.commit()
        await db.refresh(submission)
        return submission

    @staticmethod
    async def submit_review0(db: AsyncSession, user: User, data: Review0SubmissionCreate):
        pp = user.participant_profile
        if not pp:
            raise HTTPException(status_code=400, detail="User must belong to a team")
        if not pp.is_leader:
            raise HTTPException(status_code=403, detail="Only the team leader can submit Review 0")

        team = await db.get(Team, pp.team_id)
        if team and team.status == TeamStatus.REJECTED:
            raise HTTPException(status_code=403, detail="Your team has been eliminated.")

        config_res = await db.execute(select(EventConfig).where(EventConfig.id == 1))
        config = config_res.scalar_one_or_none()
        if not (config and config.active_windows.get("review0", False)):
            raise HTTPException(status_code=403, detail="Review 0 submissions are currently closed")

        track = await db.get(Track, data.track_id)
        if not track:
            raise HTTPException(status_code=404, detail="Selected track not found")

        ps = await db.get(ProblemStatement, data.problem_statement_id)
        if not ps:
            raise HTTPException(status_code=404, detail="Selected problem statement not found")

        if ps.track_id != data.track_id:
            raise HTTPException(status_code=400, detail="Selected problem statement does not belong to the selected track")

        # 1. Update team record with chosen Track & Problem Statement
        if team:
            team.track_id = data.track_id
            team.problem_statement_id = data.problem_statement_id

        # 2. Record Review 0 Submission (Title + PPT link + Description)
        r0_stmt = select(Submission).where(
            Submission.team_id == pp.team_id,
            Submission.type == "review0"
        ).order_by(Submission.submission_id.desc())
        r0_res = await db.execute(r0_stmt)
        existing_r0 = r0_res.scalars().first()

        links_data: Dict[str, Any] = {
            "ppt": data.ppt_link.strip(),
            "presentation": data.ppt_link.strip(),
        }

        if existing_r0:
            existing_r0.title = data.title.strip()
            existing_r0.description = data.description.strip() if data.description else None
            existing_r0.links = links_data
            existing_r0.status = SubmissionStatus.SUBMITTED
            existing_r0.submitted_by = user.user_id
        else:
            new_sub = Submission(
                team_id=pp.team_id,
                submitted_by=user.user_id,
                type="review0",
                title=data.title.strip(),
                description=data.description.strip() if data.description else None,
                links=links_data,
                status=SubmissionStatus.SUBMITTED
            )
            db.add(new_sub)

        await db.commit()
        if team:
            await db.refresh(team)

        return {
            "success": True,
            "message": "Review 0: Track, Problem Statement, Project Title & PPT submitted successfully",
            "team_id": team.team_id if team else pp.team_id,
            "track_id": data.track_id,
            "track_name": track.name,
            "problem_statement_id": data.problem_statement_id,
            "problem_statement_title": ps.title,
            "title": data.title,
            "ppt_link": data.ppt_link
        }

    @staticmethod
    async def submit_review1(db: AsyncSession, user: User, data: Review1SubmissionCreate):
        pp = user.participant_profile
        if not pp:
            raise HTTPException(status_code=400, detail="User must belong to a team")

        # Inherit title, description, ppt from Review 0
        r0_stmt = select(Submission).where(
            Submission.team_id == pp.team_id,
            Submission.type == "review0"
        ).order_by(Submission.submission_id.desc())
        r0_res = await db.execute(r0_stmt)
        r0_sub = r0_res.scalars().first()

        r0_links = r0_sub.links if (r0_sub and r0_sub.links) else {}
        final_title = data.title or (r0_sub.title if r0_sub and r0_sub.title else "Review 1 Submission")
        final_description = data.description or (r0_sub.description if r0_sub and r0_sub.description else "")
        final_ppt = data.ppt_link or r0_links.get("ppt") or r0_links.get("presentation") or ""

        links: Dict[str, Any] = {
            "github": data.github_link.strip(),
            "figma": data.figma_link.strip(),
        }
        if final_ppt:
            links["ppt"] = final_ppt
            links["presentation"] = final_ppt

        return await SubmissionService.create_submission(db, user, SubmissionCreate(
            type="review1",
            title=final_title,
            description=final_description,
            links=links
        ))

    @staticmethod
    async def submit_review2(db: AsyncSession, user: User, data: Review2SubmissionCreate):
        pp = user.participant_profile
        if not pp:
            raise HTTPException(status_code=400, detail="User must belong to a team")
        
        # Look up existing Review 1 or Review 0 submission for this team to inherit title, description, ppt
        r1_stmt = select(Submission).where(
            Submission.team_id == pp.team_id,
            Submission.type == "review1"
        ).order_by(Submission.submission_id.desc())
        r1_res = await db.execute(r1_stmt)
        r1_sub = r1_res.scalars().first()

        r0_stmt = select(Submission).where(
            Submission.team_id == pp.team_id,
            Submission.type == "review0"
        ).order_by(Submission.submission_id.desc())
        r0_res = await db.execute(r0_stmt)
        r0_sub = r0_res.scalars().first()

        r1_links = r1_sub.links if (r1_sub and r1_sub.links) else {}
        r0_links = r0_sub.links if (r0_sub and r0_sub.links) else {}

        final_title = data.title or (r1_sub.title if r1_sub and r1_sub.title else (r0_sub.title if r0_sub and r0_sub.title else "Review 2 Final Submission"))
        final_description = data.description or (r1_sub.description if r1_sub and r1_sub.description else (r0_sub.description if r0_sub and r0_sub.description else ""))
        final_ppt = data.ppt_link or r1_links.get("ppt") or r0_links.get("ppt") or ""

        links: Dict[str, Any] = {
            "github": data.github_link.strip(),
            "figma": data.figma_link.strip(),
        }
        if final_ppt:
            links["ppt"] = final_ppt
            links["presentation"] = final_ppt
        if data.live_url and data.live_url.strip():
            links["live_url"] = data.live_url.strip()

        return await SubmissionService.create_submission(db, user, SubmissionCreate(
            type="review2",
            title=final_title,
            description=final_description,
            links=links
        ))

    @staticmethod
    async def update_submission(db: AsyncSession, submission_id: int, user: User, data: SubmissionUpdate):
        pp = user.participant_profile
        submission = await db.get(Submission, submission_id)
        if not pp or not submission or submission.team_id != pp.team_id:
            raise HTTPException(status_code=404, detail="Submission not found or unauthorized")
        if not pp.is_leader:
            raise HTTPException(status_code=403, detail="Only team leader can modify submission")

        team = await db.get(Team, pp.team_id)
        if team and team.status == TeamStatus.REJECTED:
            raise HTTPException(status_code=403, detail="Your team has been eliminated.")

        if data.title: submission.title = data.title
        if data.description: submission.description = data.description
        links_data = submission.links or {}
        if data.links: links_data.update(data.links)
        submission.links = links_data
        await db.commit()
        await db.refresh(submission)
        return submission
