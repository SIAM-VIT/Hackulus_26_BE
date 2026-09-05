from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Any

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., pattern=r"^\d{2}[A-Z]{3}\d{4}$")
    team_name: str
    track_id: int
    is_leader: bool = False
    extra_info: Optional[Any] = None

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, v: str) -> str:
        if not v.lower().endswith("@vitstudent.ac.in"):
            raise ValueError("Email must end with @vitstudent.ac.in")
        return v.lower()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, v: str) -> str:
        if not v.lower().endswith("@vitstudent.ac.in"):
            raise ValueError("Email must end with @vitstudent.ac.in")
        return v.lower()

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
