from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.review import Review


class Panel(Base):
    __tablename__ = "panels"

    panel_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    judges: Mapped[List["User"]] = relationship("User", back_populates="panel")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="panel")
