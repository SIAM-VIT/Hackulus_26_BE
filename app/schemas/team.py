from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any

class TeamMemberCreate(BaseModel):
    name: str
    email: EmailStr
    registration_number: Optional[str] = None
    password: Optional[str] = None  # Defaults to registration_number if omitted
    hostel_block: Optional[str] = None
    is_leader: bool = False
    extra_info: Optional[Dict[str, Any]] = None

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, v: str) -> str:
        if not v.lower().endswith("@vitstudent.ac.in"):
            raise ValueError("Email must end with @vitstudent.ac.in")
        return v.lower()

class AdminCreateTeamRequest(BaseModel):
    team_name: str
    track_id: Optional[int] = None
    problem_statement_id: Optional[int] = None
    members: List[TeamMemberCreate]

# Alias for backwards compatibility
SuperAdminCreateTeamRequest = AdminCreateTeamRequest

class TeamAssignTrack(BaseModel):
    track_id: Optional[int] = None

class TeamBatchStatusUpdate(BaseModel):
    team_ids: List[int]
    status: str  # shortlisted, rejected, pending, accepted

# Alias for backwards compatibility
TeamAssignTrackPanel = TeamAssignTrack

class ProblemStatementSummary(BaseModel):
    id: int
    title: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class TeamResponse(BaseModel):
    team_id: int
    team_name: str
    track_id: Optional[int] = None
    problem_statement_id: Optional[int] = None
    status: str

    class Config:
        from_attributes = True
