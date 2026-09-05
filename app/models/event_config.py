from datetime import datetime
from typing import Dict, Any
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class EventConfig(Base):
    __tablename__ = "event_config"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    current_phase: Mapped[str] = mapped_column(String(100), default="Participants reach")
    active_windows: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        default={"review0": False, "review1": False, "review2": False}
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
