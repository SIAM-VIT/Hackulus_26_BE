from pydantic import BaseModel
from typing import Optional

class PanelCreate(BaseModel):
    name: str
    track_id: Optional[int] = None

class PanelResponse(BaseModel):
    panel_id: int
    name: str
    track_id: Optional[int] = None

    class Config:
        from_attributes = True
