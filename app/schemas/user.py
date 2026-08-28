from pydantic import BaseModel, EmailStr
from typing import Optional, Any

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    team_id: Optional[int] = None
    panel_id: Optional[int] = None
    is_leader: bool = False
    extra_info: Optional[Any] = None

    class Config:
        from_attributes = True

class UserDetailResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    is_leader: bool
    extra_info: Optional[Any] = None

    class Config:
        from_attributes = True
