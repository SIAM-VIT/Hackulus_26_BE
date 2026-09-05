from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class ReviewCreateUpdate(BaseModel):
    submission_id: Optional[int] = None
    team_id: Optional[int] = None
    panel_id: Optional[int] = None
    track_id: Optional[int] = None
    review_round: Optional[str] = None  # review1, review2
    
    # 6 Scoring Categories
    innovation_score: Optional[float] = Field(0.0, ge=0, le=100)
    technical_complexity_score: Optional[float] = Field(0.0, ge=0, le=100)
    feasibility_score: Optional[float] = Field(0.0, ge=0, le=100)
    ui_ux_score: Optional[float] = Field(0.0, ge=0, le=100)
    presentation_score: Optional[float] = Field(0.0, ge=0, le=100)
    progress_score: Optional[float] = Field(0.0, ge=0, le=100)

    score: Optional[float] = Field(None, ge=0)  # Optional manual override or computed
    comments: Optional[str] = None
    set_team_status: Optional[str] = None  # e.g. "shortlisted", "rejected"

class ReviewResponse(BaseModel):
    review_id: int
    submission_id: int
    team_id: Optional[int] = None
    judge_id: Optional[int] = None
    judge_name: Optional[str] = None
    panel_id: Optional[int] = None
    track_id: Optional[int] = None
    review_round: Optional[str] = None
    
    innovation_score: Optional[float] = 0.0
    technical_complexity_score: Optional[float] = 0.0
    feasibility_score: Optional[float] = 0.0
    ui_ux_score: Optional[float] = 0.0
    presentation_score: Optional[float] = 0.0
    progress_score: Optional[float] = 0.0
    
    score: Optional[float] = None
    comments: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
