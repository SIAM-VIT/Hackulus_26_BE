from pydantic import BaseModel, EmailStr
from typing import Optional, Any, Dict
from datetime import datetime


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    panel_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ParticipantProfileResponse(BaseModel):
    registration_number: Optional[str] = None
    hostel_block: Optional[str] = None
    is_leader: bool = False
    team_id: int
    extra_info: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class UserDetailResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    panel_id: Optional[int] = None
    participant_profile: Optional[ParticipantProfileResponse] = None

    class Config:
        from_attributes = True
