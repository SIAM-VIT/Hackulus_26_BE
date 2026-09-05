from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Numeric, Text, ForeignKey, DateTime, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.submission import Submission
    from app.models.user import User
    from app.models.track import Track
    from app.models.team import Team
    from app.models.panel import Panel

class Review(Base):
    __tablename__ = "reviews"

    review_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.submission_id", ondelete="CASCADE"), nullable=False)
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.team_id", ondelete="CASCADE"))
    judge_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"))
    panel_id: Mapped[Optional[int]] = mapped_column(ForeignKey("panels.panel_id", ondelete="SET NULL"))
    track_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tracks.track_id", ondelete="SET NULL"))
    review_round: Mapped[Optional[str]] = mapped_column(String(50))  # review1, review2
    
    # 6 Scoring Categories
    innovation_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), default=0.0)
    technical_complexity_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), default=0.0)
    feasibility_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), default=0.0)
    ui_ux_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), default=0.0)
    presentation_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), default=0.0)
    progress_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), default=0.0)
    
    score: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), default=0.0)  # Total score
    comments: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    submission: Mapped["Submission"] = relationship("Submission", back_populates="reviews")
    judge: Mapped[Optional["User"]] = relationship("User", back_populates="reviews")
    team: Mapped[Optional["Team"]] = relationship("Team")
    panel: Mapped[Optional["Panel"]] = relationship("Panel", back_populates="reviews")

    __table_args__ = (
        UniqueConstraint("submission_id", "judge_id", name="unique_submission_judge"),
    )
