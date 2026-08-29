from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

class TeamMemberCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    registration_number: Optional[str] = None
    hostel_block: Optional[str] = None
    is_leader: bool = False
    extra_info: Optional[Dict[str, Any]] = None

class AdminCreateTeamRequest(BaseModel):
    team_name: str
    track_id: Optional[int] = None
    problem_statement: Optional[str] = None
    idea: Optional[str] = None
    members: List[TeamMemberCreate]

# Alias for backwards compatibility
SuperAdminCreateTeamRequest = AdminCreateTeamRequest

class TeamAssignTrack(BaseModel):
    track_id: Optional[int] = None

# Alias for backwards compatibility
TeamAssignTrackPanel = TeamAssignTrack

class TeamResponse(BaseModel):
    team_id: int
    team_name: str
    problem_statement: Optional[str] = None
    idea: Optional[str] = None
    track_id: Optional[int] = None
    status: str

    class Config:
        from_attributes = True
