from datetime import datetime
from pydantic import BaseModel


class EntryDetailCreate(BaseModel):
    entrada_id: int
    producto_id: int
    cantidad: int
    costo_unitario: float


class EntryDetailResponse(EntryDetailCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}