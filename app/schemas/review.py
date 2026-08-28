from pydantic import BaseModel, Field
from typing import Optional

class ReviewCreateUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=100)
    comments: Optional[str] = None
    panel_id: Optional[int] = None
    track_id: Optional[int] = None
    set_team_status: Optional[str] = None

class ReviewResponse(BaseModel):
    review_id: int
    submission_id: int
    judge_id: Optional[int] = None
    panel_id: Optional[int] = None
    track_id: Optional[int] = None
    score: Optional[float] = None
    comments: Optional[str] = None

    class Config:
        from_attributes = True
