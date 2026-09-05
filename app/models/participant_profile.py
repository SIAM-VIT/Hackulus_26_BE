from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.team import Team


class ParticipantProfile(Base):
    """
    Stores participant-specific data. Only exists for users with role=PARTICIPANT.
    Eliminates all participant-blob nulls from the users table.
    """
    __tablename__ = "participant_profiles"

    profile_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        unique=True, nullable=False
    )
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.team_id", ondelete="CASCADE"),
        nullable=False
    )
    is_leader: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Optional: data may arrive after registration
    registration_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    hostel_block: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    extra_info: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    user: Mapped["User"] = relationship("User", back_populates="participant_profile")
    team: Mapped["Team"] = relationship("Team", back_populates="members")
