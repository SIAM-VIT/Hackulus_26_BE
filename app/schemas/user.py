from pydantic import BaseModel, EmailStr
from typing import Optional, Any

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    registration_number: Optional[str] = None
    hostel_block: Optional[str] = None
    team_id: Optional[int] = None
    is_leader: bool = False
    extra_info: Optional[Any] = None

    class Config:
        from_attributes = True

class UserDetailResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    registration_number: Optional[str] = None
    hostel_block: Optional[str] = None
    is_leader: bool = False
    extra_info: Optional[Any] = None

    class Config:
        from_attributes = True
