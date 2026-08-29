from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.team import Team
    from app.models.problem_statement import ProblemStatement

class Track(Base):
    __tablename__ = "tracks"

    track_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    teams: Mapped[List["Team"]] = relationship("Team", back_populates="track")
    problem_statements: Mapped[List["ProblemStatement"]] = relationship("ProblemStatement", back_populates="track", cascade="all, delete-orphan")

