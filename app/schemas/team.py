from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any

class TeamMemberCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., pattern=r"^\d{2}[A-Z]{3}\d{4}$")
    is_leader: bool = False
    hostel_block: Optional[str] = None
    extra_info: Optional[Dict[str, Any]] = None

class AdminCreateTeamRequest(BaseModel):
    team_name: str
    track_id: Optional[int] = None
    panel_id: Optional[int] = None
    problem_statement: Optional[str] = None
    idea: Optional[str] = None
    members: List[TeamMemberCreate]

# Alias for backwards compatibility
SuperAdminCreateTeamRequest = AdminCreateTeamRequest

class TeamAssignTrackPanel(BaseModel):
    track_id: Optional[int] = None
    panel_id: Optional[int] = None

class TeamResponse(BaseModel):
    team_id: int
    team_name: str
    problem_statement: Optional[str] = None
    idea: Optional[str] = None
    track_id: Optional[int] = None
    panel_id: Optional[int] = None
    status: str

    class Config:
        from_attributes = True
