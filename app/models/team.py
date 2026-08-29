from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.track import Track
    from app.models.user import User
    from app.models.submission import Submission

class TeamStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SHORTLISTED = "shortlisted"

class Team(Base):
    __tablename__ = "teams"

    team_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_name: Mapped[str] = mapped_column(String(200), nullable=False)
    problem_statement: Mapped[Optional[str]] = mapped_column(Text)
    idea: Mapped[Optional[str]] = mapped_column(Text)
    track_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tracks.track_id", ondelete="CASCADE"))
    status: Mapped[TeamStatus] = mapped_column(String(32), default=TeamStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    track: Mapped[Optional["Track"]] = relationship("Track", back_populates="teams")
    members: Mapped[List["User"]] = relationship("User", back_populates="team")
    submissions: Mapped[List["Submission"]] = relationship("Submission", back_populates="team")
