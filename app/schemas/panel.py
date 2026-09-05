from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class PanelBase(BaseModel):
    name: str
    description: Optional[str] = None

class PanelCreate(PanelBase):
    pass

class PanelResponse(PanelBase):
    panel_id: int
    created_at: Optional[datetime] = None
    judges_count: Optional[int] = 0

    class Config:
        from_attributes = True
