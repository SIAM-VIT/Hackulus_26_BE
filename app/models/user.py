from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.participant_profile import ParticipantProfile
    from app.models.panel import Panel
    from app.models.review import Review


class UserRole(str, Enum):
    PARTICIPANT = "participant"
    JUDGE = "judge"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(50), nullable=False, default=UserRole.PARTICIPANT)
    # panel_id: only meaningful for judges — 1 nullable field is acceptable
    panel_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("panels.panel_id", ondelete="SET NULL"), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Participant-specific data lives in participant_profiles (3NF)
    participant_profile: Mapped[Optional["ParticipantProfile"]] = relationship(
        "ParticipantProfile", back_populates="user", uselist=False
    )
    panel: Mapped[Optional["Panel"]] = relationship("Panel", back_populates="judges")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="judge")
