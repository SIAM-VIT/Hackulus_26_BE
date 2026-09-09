from pydantic import BaseModel
from typing import Optional, Dict, Any

class SubmissionCreate(BaseModel):
    type: str  # review0, review1, review2, final
    title: Optional[str] = None
    description: Optional[str] = None
    links: Optional[Dict[str, Any]] = None  # e.g., {"github": "https://...", "ppt": "https://..."}

class Review0SubmissionCreate(BaseModel):
    track_id: int
    problem_statement_id: int

class Review1SubmissionCreate(BaseModel):
    title: str
    description: str
    github_link: str
    ppt_link: str
    figma_link: Optional[str] = None

class Review2SubmissionCreate(BaseModel):
    title: str
    description: str
    github_link: str
    ppt_link: str
    live_url: str
    figma_link: Optional[str] = None

class SubmissionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    links: Optional[Dict[str, Any]] = None

class SubmissionResponse(BaseModel):
    submission_id: int
    team_id: int
    submitted_by: Optional[int] = None
    type: str
    title: Optional[str] = None
    description: Optional[str] = None
    links: Optional[Dict[str, Any]] = None
    status: str

    class Config:
        from_attributes = True
