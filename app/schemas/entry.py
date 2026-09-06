from datetime import datetime
from pydantic import BaseModel


class EntryCreate(BaseModel):
    sucursal_id: int
    usuario_id: int


class EntryResponse(EntryCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}