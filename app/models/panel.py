from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.track import Track
    from app.models.team import Team
    from app.models.user import User

class Panel(Base):
    __tablename__ = "panels"

    panel_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    track_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tracks.track_id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    track: Mapped[Optional["Track"]] = relationship("Track", back_populates="panels")
    teams: Mapped[List["Team"]] = relationship("Team", back_populates="panel")
    judges: Mapped[List["User"]] = relationship("User", back_populates="panel")
