from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., pattern=r"^\d{2}[A-Z]{3}\d{4}$")
    team_name: str
    track_id: int
    is_leader: bool = False
    extra_info: Optional[Any] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
