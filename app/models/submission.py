from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.team import Team
    from app.models.review import Review

class SubmissionType(str, Enum):
    REVIEW1 = "review1"
    REVIEW2 = "review2"
    FINAL = "final"

class SubmissionStatus(str, Enum):
    SUBMITTED = "submitted"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Submission(Base):
    __tablename__ = "submissions"

    submission_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id", ondelete="CASCADE"), nullable=False)
    submitted_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"))
    type: Mapped[SubmissionType] = mapped_column(String(50), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    links: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    status: Mapped[SubmissionStatus] = mapped_column(String(50), default=SubmissionStatus.SUBMITTED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    team: Mapped["Team"] = relationship("Team", back_populates="submissions")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="submission")
