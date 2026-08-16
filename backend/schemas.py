from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LinkCreate(BaseModel):
    target_url: str
    
class LinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    target_url: str
    clicks: int
    created_at: datetime