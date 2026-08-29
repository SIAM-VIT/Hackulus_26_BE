from pydantic import BaseModel
from typing import Optional, Dict, Any

class SubmissionCreate(BaseModel):
    type: str  # review1, review2, final
    title: Optional[str] = None
    description: Optional[str] = None
    links: Optional[Dict[str, Any]] = None  # e.g., {"ppt": "https://...", "github": "..."}
    track_id: Optional[int] = None
    problem_statement: Optional[str] = None

class SubmissionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    links: Optional[Dict[str, Any]] = None
    track_id: Optional[int] = None
    problem_statement: Optional[str] = None

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
