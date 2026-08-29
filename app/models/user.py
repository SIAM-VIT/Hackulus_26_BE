from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.team import Team
    from app.models.review import Review

class UserRole(str, Enum):
    PARTICIPANT = "participant"
    JUDGE = "judge"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    registration_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(50), default=UserRole.PARTICIPANT)
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.team_id", ondelete="SET NULL"))
    is_leader: Mapped[bool] = mapped_column(Boolean, default=False)
    extra_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    hostel_block: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="members")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="judge")
